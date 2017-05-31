from dsa_g4z3 import dsa_gen_key, dsa_verify, DSAConfig
import random
from math_g4z3 import mod_exp, mod_mult, inv_mod, mod_add
from converts import ez_hash, bin_str_to_big_int, big_int_to_bin_str
import hashlib

msgs = ['I am a sample message.', 'Me too, another sample message.', 'Plus me!']
ds = [bin_str_to_big_int(ez_hash(hashlib.sha1, msg)) for msg in msgs]


def rougue_sign(d_, x_, c_, l_, k_=None):
    k = k_ or random.randrange(1, c_.q)
    r = mod_exp(c_.g, k, c_.p) % c_.q
    s = mod_mult(inv_mod(k, c_.q), mod_add(d_, mod_mult(x_, r, c_.q), c_.q), c_.q)
    if l_:
        return r, s, k
    else:
        return r, s


def forge_0():
    return 0, random.randrange(1, 999999999999)


def crack_0():
    conf = DSAConfig(g=0)
    x, y = dsa_gen_key(conf)
    for i in range(len(msgs)):
        print 'Message:{msg}'.format(msg=msgs[i])
        r, s = rougue_sign(ds[i], x, conf, False)
        print 'Signature: r={r:x}, s={s:x}'.format(r=r, s=s)
        r_, s_ = forge_0()
        print 'Forged signature: r={r:x}, s={s:x}'.format(r=r_, s=s_)
        v_ = dsa_verify(msgs[i], r_, s_, y, conf, rougue=True)
        assert v_, "Forged signature verification failed"
        print "Forged signature verify {vv}".format(vv='OK' if v_ else 'Failed')


def forge_1(y, conf):
    z = random.randrange(1, 99999)
    r = mod_exp(y, z, conf.p) % conf.q
    s = mod_mult(r, inv_mod(z, conf.q), conf.q)
    return r, s, z


def crack_1():
    conf = DSAConfig(g=1)
    x, y = dsa_gen_key(conf)
    print "Generated key x={x:x}, y={y:x}".format(x=x, y=y)
    n_round = 10
    for i in range(n_round):
        r, s, z = forge_1(y, conf)
        print "Forged signature r={r:x}, s={s:x}, z={z:x}".format(r=r, s=s, z=z)
        for m in msgs:
            v = dsa_verify(m, r, s, y, conf)
            assert v, 'Forged signature verification failed'
            print "Forged signature verify {vv}".format(vv='OK' if v else 'Failed')


def crack():
    crack_0()
    crack_1()
