from srp import SRPClient, SRPDefaultConfig, get_key_proof
from utils import mod_exp, mod_add, mod_mult
from converts import sha256, bin_str_to_big_int, big_int_to_bin_str
import random
import sys


class PasswordDict:
    def __init__(self, max_len):
        """
        :param max_len: number of bytes
         must have max_len < 2
        """
        self.max = (1 << (max_len * 8)) - 1
        self.next_val = 0

    def __iter__(self):
        return self

    @staticmethod
    def format_value(v):
        return format(v, "0=4x")

    def next(self):
        if self.next_val > self.max:
            raise StopIteration()
        ret = self.format_value(self.next_val)
        self.next_val += 1
        return ret

    def get_random(self):
        return self.format_value(random.randrange(self.max))

    def debug_mode(self, next_val):
        self.next_val = int(next_val, 16)


class SRPServerHack:
    def __init__(self, password_len):
        self.config = SRPDefaultConfig()
        self.pd = PasswordDict(password_len)

    def auth_begin(self, identity, pkc):
        self.pkc = pkc
        self.salt = "hack_salt"
        self.b = random.randrange(self.config.N)
        self.pks = mod_exp(self.config.g, self.b, self.config.N)
        self.u = bin_str_to_big_int(sha256(self.pkc, self.pks))
        return self.salt, self.pks

    def auth_finish(self, identity, proof):
        print "Cracking..."
        for password in self.pd:
            if password[-1] == "0":
                print "Trying {p}\r".format(p=password),
                sys.stdout.flush()
            x = bin_str_to_big_int(sha256(self.salt, password))
            v = mod_exp(self.config.g, x, self.config.N)
            tmp = mod_exp(v, self.u, self.config.N)
            tmp = mod_mult(self.pkc, tmp, self.config.N)
            s = mod_exp(tmp, self.b, self.config.N)
            k = sha256(s)
            my_proof = get_key_proof(k, self.salt)
            if my_proof == proof:
                print "Cracked, password={p}".format(p=password)
                return "OK"
        print "Crack failed"
        return "Failed"


def run():
    server = SRPServerHack(1)
    identity = "portal@IO2A.com"
    password = server.pd.get_random()
    print "Pre-selected random password {p}".format(p=password)
    client = SRPClient(server)
    client.auth_simplified(identity, password)


run()
