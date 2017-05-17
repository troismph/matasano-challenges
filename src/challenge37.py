from srp import SRPClient, SRPServer, SRPDefaultConfig
from converts import big_int_to_bin_str
import os


def reg(server, identity, password):
    """
    
    :param server:
    :type server: SRPServer 
    :param identity: 
    :param password: 
    :return: 
    """
    client = SRPClient(server)
    client.reg(identity, password)


def auth(server, identity, password):
    client = SRPClient(server)
    client.auth(identity, password)
    return client


def auth_hack(server, identity, pkc):
    client = SRPClient(server)
    client.auth_hack(identity, pkc)
    return client


def run():
    pkc = 0
    server = SRPServer()
    # register
    identity = "my_identity"
    password = os.urandom(32)
    reg(server, identity, password)
    # log in with correct password
    client = auth(server, identity, password)
    assert client.get_session_key() == server.get_session_key(identity), "Error auth with correct password"
    # log in with no password and pkc = n*N where n iterates in range(10)
    default_conf = SRPDefaultConfig()
    for x in range(10):
        pkc = x * default_conf.N
        cx = auth_hack(server, identity, pkc)
        assert cx.get_session_key() == server.get_session_key(identity), "Hack auth failed"
        print "Hack auth with pkc={pkc} passed".format(pkc=pkc)
        print "Session key on client={sk}".format(sk=cx.get_session_key().encode('hex'))
        print "Session key on server={sk}".format(sk=server.get_session_key(identity).encode('hex'))
    print "All pass"


run()
