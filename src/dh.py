from utils import mod_exp
import random


DH_p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
DH_g = 2


class DHClient:
    def __init__(self):
        self.priv_key = random.randrange(DH_p)
        self.pub_key = mod_exp(DH_g, self.priv_key, DH_p)

    def get_shared_key(self, pub_key):
        return mod_exp(pub_key, self.priv_key, DH_p)


def test_dh():
    rounds = 10
    test_pass = True
    for x in range(rounds):
        dha = DHClient()
        dhb = DHClient()
        sa = dha.get_shared_key(dhb.pub_key)
        sb = dhb.get_shared_key(dha.pub_key)
        if sa != sb:
            print "Test fail"
            test_pass = False
    if test_pass:
        print "Test pass with {n} cases".format(n=rounds)