# Implementation of the Secure Remote Password protocol
# Please refer to https://en.wikipedia.org/wiki/Secure_Remote_Password_protocol
import random
import os
import hmac
import hashlib
from utils import mod_exp, mod_add, mod_mult
from converts import bin_str_to_big_int, big_int_to_bin_str, sha256


class SRPDefaultConfig:
    def __init__(self):
        self.N = int(
            "00b51d108d00cc05c9d39f99758030841903982ad98b8e260929ba07931db766126607836ba3ba29cda2f8616b53c0a2554516c3003e362aba18e69af83b87d84e0af042b54f08e42ddea35b5d65835ceffb2253cdc9d7f487546541c2d64d521c931f5a75ffc5def3653e23f9d9561ad16c5db126d85e8e4b894af25267f7b133",
            16)
        self.g = 2
        self.k = 3


def get_key_proof(key, common_knowledge):
    h = hmac.new(key, common_knowledge, hashlib.sha256)
    return h.digest()


class SRPServer:
    def __init__(self, config=None):
        if config is None:
            config = SRPDefaultConfig()
        self.config = config
        self.registry = {}

    def reg(self, identity, salt, verifier):
        if identity in self.registry:
            raise Exception("Identity already registered")
        self.registry[identity] = {"salt": salt, "verifier": verifier, "session": {}}

    def auth_begin(self, identity, pkc):
        if identity not in self.registry:
            raise Exception("Identity not found")
        entry = self.registry[identity]
        # first clear previous session
        entry["session"] = {}
        entry["session"]["pkc"] = pkc
        entry["session"]["b"] = random.randrange(self.config.N)
        entry["session"]["pks"] = mod_add(mod_mult(self.config.k, entry["verifier"], self.config.N),
                                          mod_exp(self.config.g, entry["session"]["b"], self.config.N), self.config.N)
        return entry["salt"], entry["session"]["pks"]

    def auth_finish(self, identity, proof):
        if identity not in self.registry:
            raise Exception("Identity not found")
        entry = self.registry[identity]
        u_str = sha256(entry["session"]["pkc"], entry["session"]["pks"])
        entry["session"]["u"] = bin_str_to_big_int(u_str)
        tmp = mod_exp(entry["verifier"], entry["session"]["u"], self.config.N)
        tmp = mod_mult(entry["session"]["pkc"], tmp, self.config.N)
        tmp = mod_exp(tmp, entry["session"]["b"], self.config.N)
        sk = sha256(tmp)
        my_proof = get_key_proof(sk, entry["salt"])
        # for now, proof is session-key itself
        if my_proof == proof:
            entry["session"]["key"] = sk
            return "OK"
        else:
            return "Failed"

    def get_session_key(self, identity):
        if identity not in self.registry:
            raise Exception("Identity not found")
        entry = self.registry[identity]
        if "key" not in entry["session"]:
            raise Exception("Session uninitialized")
        return entry["session"]["key"]


class SRPClient:
    def __init__(self, server, config=None):
        """
        
        :param server:
        :type server: SRPServer
        :param config: 
        """
        self.server = server
        if config is None:
            config = SRPDefaultConfig()
        self.config = config
        self.session = {}

    def reg(self, identity, password):
        salt = os.urandom(64)
        x = bin_str_to_big_int(sha256(salt, password))
        verifier = mod_exp(self.config.g, x, self.config.N)
        self.server.reg(identity, salt, verifier)

    def auth(self, identity, password):
        if len(self.session) > 0:
            raise Exception("Cannot re-use authenticated client")
        self.session["a"] = random.randrange(self.config.N)
        self.session["pkc"] = mod_exp(self.config.g, self.session["a"], self.config.N)
        self.session["salt"], self.session["pks"] = self.server.auth_begin(identity, self.session["pkc"])
        u = bin_str_to_big_int(sha256(self.session["pkc"], self.session["pks"]))
        x = bin_str_to_big_int(sha256(self.session["salt"], password))
        tmp = mod_exp(self.config.g, x, self.config.N)
        tmp = mod_mult(self.config.k, tmp, self.config.N)
        tmp = mod_add(self.session["pks"], -tmp, self.config.N)
        tmp = mod_exp(tmp, (self.session["a"] + u * x), self.config.N)
        self.session["key"] = sha256(tmp)
        proof = get_key_proof(self.session["key"], self.session["salt"])
        ret = self.server.auth_finish(identity, proof)
        if ret != "OK":
            raise Exception("Auth failed")

    def auth_hack(self, identity, pkc):
        if len(self.session) > 0:
            raise Exception("Cannot re-use authenticated client")
        self.session["a"] = random.randrange(self.config.N)
        self.session["salt"], self.session["pks"] = self.server.auth_begin(identity, pkc)
        self.session["key"] = sha256(0L)
        proof = get_key_proof(self.session["key"], self.session["salt"])
        ret = self.server.auth_finish(identity, proof)
        if ret != "OK":
            raise Exception("Hack auth failed")

    def get_session_key(self):
        if "key" not in self.session:
            raise Exception("Unauthenticated client")
        return self.session["key"]


def test_srp():
    identity = "test_identity"
    password = os.urandom(32)
    server = SRPServer()
    client = SRPClient(server)
    client.reg(identity, password)
    client2 = SRPClient(server)
    client2.auth(identity, password)
    print "Client Key {ck}\nServer Key {sk}".format(ck=client2.get_session_key().encode('hex'),
                                                    sk=server.get_session_key(identity).encode('hex'))
    if client2.get_session_key() == server.get_session_key(identity):
        print "Test pass"
    else:
        print "Test fail!!!!!!!!!!!!!!!!!!!!"
