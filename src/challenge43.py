from dsa_g4z3 import dsa_gen_key, dsa_sign, dsa_verify, DSAConfig, try_sign
from math_g4z3 import mod_mult, mod_add, inv_mod
from converts import bin_str_to_big_int, ez_hash, big_int_to_bin_str
import sys
import os
import random
import hashlib


def crack_by_k(r, s, k, h, q):
    inv_r = inv_mod(r, q)
    x = mod_mult(s * k - h, inv_r, q)
    return x


def test_crack_by_k():
    dsa_conf = DSAConfig()
    n_round = 10
    for i in range(n_round):
        print "\r" + " " * 100,
        print "\rRound{n}, Generating dsa key pair...".format(n=i),
        sys.stdout.flush()
        x, y = dsa_gen_key(dsa_conf)
        print "Done",
        sys.stdout.flush()
        msg = os.urandom(random.randrange(7, 2000)).encode('hex')
        print "Verifying",
        sys.stdout.flush()
        r, s, k = dsa_sign(msg, x, dsa_conf, True)
        h = bin_str_to_big_int(ez_hash(hashlib.sha1, msg))
        x_ = crack_by_k(r, s, k, h, dsa_conf.q)
        assert x == x_, "Failed to find secret key, need\n{x}\nget\n{x_}".format(x=x, x_=x_)
        print "OK"
    print "Pass after {n} rounds".format(n=n_round)


def verify_keys(x, y, conf):
    msg = os.urandom(random.randrange(7, 2000)).encode('hex')
    r, s = dsa_sign(msg, x, conf)
    return dsa_verify(msg, r, s, y, conf)


# I can brute-force k and deduce x,
# but my sha1(x) doesn't match that on the cryptopal's web page.
# The given message's sha1 doesn't match either.
# Whatever, my x, together with the given y, creates matching signature,
# so I consider this as a "Pass".
def crack():
    dsa_conf = DSAConfig()
    h = 0xd2d0714f014a9784047eaeccf956520045c45265
    r = 548099063082341131477253921760299949438196259240
    s = 857042759984254168557880549501802188789837994940
    y = int("84ad4719d044495496a3201c8ff484feb45b962e7302e56a392aee4"\
            "abab3e4bdebf2955b4736012f21a08084056b19bcd7fee56048e004"\
            "e44984e2f411788efdc837a0d2e5abb7b555039fd243ac01f0fb2ed"\
            "1dec568280ce678e931868d23eb095fde9d3779191b8c0299d6e07b"\
            "bb283e6633451e535c45513b2d33c99ea17", 16)
    # now let's brute!
    print " " * 60 + "\r"
    for k in xrange(1 << 16):
        if k & 0xff == 0xff:
            print "\rTrying {k}".format(k=hex(k)),
            sys.stdout.flush()
        x_ = crack_by_k(r, s, k, h, dsa_conf.q)
        r_, s_ = try_sign(h, x_, dsa_conf, False, k)
        if r_ == r and s_ == s:
            print "\nFound!, k={k}".format(k=hex(k))
            print "Private key={x}".format(x=hex(x_))
            fp = ez_hash(hashlib.sha1, big_int_to_bin_str(x_).encode('hex'))
            print "SHA-1 fingerprint={f}".format(f=fp.encode('hex'))
            if verify_keys(x_, y, dsa_conf):
                print "Keys verified"
            else:
                print "Keys verify failed"
            return
    print "\nFailed to find k"
