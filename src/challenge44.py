from math_g4z3 import mod_mult, mod_add, inv_mod
from challenge43 import crack_by_k, verify_keys
from converts import bin_str_to_big_int, big_int_to_bin_str, ez_hash
from dsa_g4z3 import DSAConfig, dsa_gen_key, dsa_sign, dsa_verify, try_sign
import hashlib

y = int('2d026f4bf30195ede3a088da85e398ef869611d0f68f07'
        '13d51c9c1a3a26c95105d915e2d8cdf26d056b86b8a7b8'
        '5519b1c23cc3ecdc6062650462e3063bd179c2a6581519'
        'f674a61f1d89a1fff27171ebc1b93d4dc57bceb7ae2430'
        'f98a6a4d83d8279ee65d71c1203d2c96d65ebbf7cce9d3'
        '2971c3de5084cce04a2e147821', 16)


def prep_data():
    """
    :return: [msg, s, r, digest] * n 
    """
    with open('44.txt') as f:
        lines = [x.rstrip('\n').split(': ')[1] for x in f.readlines()]
        ret = [[lines[x], int(lines[x + 1], 10), int(lines[x + 2], 10), int(lines[x + 3], 16)] for x in
               range(0, len(lines), 4)]
    return ret


def find_k(d0, d1, conf):
    """
    
    :param d0: 
    :param d1: 
    :param conf:
     :type conf: DSAConfig
    :return: 
    """
    t0 = mod_add(d0[3], -d1[3], conf.q)
    t1 = mod_add(d0[1], -d1[1], conf.q)
    t2 = inv_mod(t1, conf.q)
    t3 = mod_mult(t0, t2, conf.q)
    return t3


def find_dup_k(d):
    ret = []
    for a in range(0, len(d)):
        for b in range(a):
            if d[a][2] == d[b][2]:
                ret.append([a, b])
    return ret


def crack():
    conf = DSAConfig()
    data = prep_data()
    dupk = find_dup_k(data)
    ret = []
    for pairk in dupk:
        da = data[pairk[0]]
        db = data[pairk[1]]
        k = find_k(da, db, conf)
        x = crack_by_k(da[2], da[1], k, da[3], conf.q)
        x_ = crack_by_k(db[2], db[1], k, db[3], conf.q)
        assert x == x_, "Inequal x"
        # verify x
        ra, sa = try_sign(da[3], x, conf, False, k)
        print "msg={m}".format(m=da[0])
        print "x={x}\nr={r}\ns={s}".format(x=format(x, 'x'), r=format(ra, 'x'), s=format(sa, 'x'))
        print "d={d}".format(d=da)
        assert ra == da[2], "Inequal ra"
        assert sa == da[1], "Inequal sa"
        assert verify_keys(x, y, conf)
        ret.append(x)
    for x in ret:
        print "Found x with hash={h}".format(h=ez_hash(hashlib.sha1, big_int_to_bin_str(x).encode('hex')).encode('hex'))


def ccc():
    k = 95271
    msg0 = 'I am a sample message.'
    msg1 = 'Me too!'
    h0 = bin_str_to_big_int(ez_hash(hashlib.sha1, msg0))
    h1 = bin_str_to_big_int(ez_hash(hashlib.sha1, msg1))
    conf = DSAConfig()
    x, y = dsa_gen_key(conf)
    r0, s0 = try_sign(h0, x, conf, False, k)
    r1, s1 = try_sign(h1, x, conf, False, k)
    d0 = [msg0, s0, r0, h0]
    d1 = [msg1, s1, r1, h1]
    k_ = find_k(d0, d1, conf)
    assert k == k_, "Error finding k"
    print "Found k={k_}, original={k}".format(k=k, k_=k_)
    x_ = crack_by_k(r0, s0, k, h0, conf.q)
    assert x == x_, "Error cracking by k"
    print "Found x={x_}\nOriginal x={x}".format(x_=x, x=x)
    assert verify_keys(x_, y, conf), "Error verifying keys"
    print "Verified OK"
