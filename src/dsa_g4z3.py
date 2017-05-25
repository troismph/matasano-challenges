from converts import big_int_to_bin_str, bin_str_to_big_int
from math_g4z3 import mod_exp, mod_add, inv_mod, mod_mult
from converts import ez_hash
import hashlib
import random
import sys
import os

DSA_P = int('800000000000000089e1855218a0e7dac38136ffafa72eda7' \
            '859f2171e25e65eac698c1702578b07dc2a1076da241c76c6' \
            '2d374d8389ea5aeffd3226a0530cc565f3bf6b50929139ebe' \
            'ac04f48c3c84afb796d61e5a4f9a8fda812ab59494232c7d2' \
            'b4deb50aa18ee9e132bfa85ac4374d7f9091abc3d015efc87' \
            '1a584471bb1', 16)

DSA_Q = 0xf4f47f05794b256174bba6e9b396a7707e563c5b

DSA_G = int('5958c9d3898b224b12672c0b98e06c60df923cb8bc999d119' \
            '458fef538b8fa4046c8db53039db620c094c9fa077ef389b5' \
            '322a559946a71903f990f1f7e0e025e2d7f7cf494aff1a047' \
            '0f5b64c36b625a097f1651fe775323556fe00b3608c887892' \
            '878480e99041be601a62166ca6894bdd41a7054ec89f756ba' \
            '9fc95302291', 16)


class DSAConfig:
    def __init__(self, **kwargs):
        self.p = kwargs.get('p', DSA_P)
        self.q = kwargs.get('q', DSA_Q)
        self.g = kwargs.get('g', DSA_G)


def dsa_gen_key(conf):
    x = random.randrange(1, conf.q)
    y = mod_exp(conf.g, x, conf.p)
    return x, y


def try_sign(d_, x_, c_, l_, k_=None):
    k = k_ or random.randrange(1, c_.q)
    r = mod_exp(c_.g, k, c_.p) % c_.q
    if r == 0:
        # time to retry with different k
        return None
    s = mod_mult(inv_mod(k, c_.q), mod_add(d_, mod_mult(x_, r, c_.q), c_.q), c_.q)
    if s == 0:
        # time to retry with different k
        return None
    if l_:
        return r, s, k
    else:
        return r, s


def dsa_sign(msg, x, conf, leak=False):
    digest = bin_str_to_big_int(ez_hash(hashlib.sha1, msg))
    cnt = 0
    while cnt < 10:
        ret = try_sign(digest, x, conf, leak)
        if ret is not None:
            return ret
        cnt += 1
    assert False, "Cannot find a valid signature after {n} tries".format(n=cnt)


def verify_by_digest(d, r, s, y, conf):
    w = inv_mod(s, conf.q)
    u1 = mod_mult(d, w, conf.q)
    u2 = mod_mult(r, w, conf.q)
    v = mod_mult(mod_exp(conf.g, u1, conf.p), mod_exp(y, u2, conf.p), conf.p) % conf.q
    return v == r


def dsa_verify(msg, r, s, y, conf):
    if not (0 < r < conf.q and 0 < s < conf.q):
        return False
    digest = bin_str_to_big_int(ez_hash(hashlib.sha1, msg))
    return verify_by_digest(digest, r, s, y, conf)


def test_dsa():
    dsa_conf = DSAConfig()
    n_round = 10
    for i in range(n_round):
        print "\r" + " " * 100,
        print "\rRound{n}, Generating dsa key pair...".format(n=i),
        sys.stdout.flush()
        x, y = dsa_gen_key(dsa_conf)
        print "OK",
        sys.stdout.flush()
        msg = os.urandom(random.randrange(7, 2000)).encode('hex')
        print "Verifying",
        sys.stdout.flush()
        r, s = dsa_sign(msg, x, dsa_conf)
        assert dsa_verify(msg, r, s, y, dsa_conf), "Verification failed"
        print "OK"
    print "\r" + " " * 100,
    print "\rPass after {n} rounds".format(n=n_round)
