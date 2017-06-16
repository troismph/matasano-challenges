import os
import random
import string
import sys
from converts import encrypt_aes_128_ecb, pkcs7_pad

EASY_BLOCK_LEN_BYTES = 2
HARD_BLOCK_LEN_BYTES = 4
EASY_KEY = bytearray(b'\x9es')
HARD_KEY = bytearray(b'\xbc\x78\x2f\xa2')
ALPHABET = string.ascii_letters + string.digits


def small_enc(buf, key, bl):
    """
    An AES encryption operating on BLOCK_LEN_BYTES-byte blocks 
    """
    k = bytearray(key)
    b = bytearray(buf)
    pkcs7_pad(k, 16)
    pkcs7_pad(b, 16)
    e = encrypt_aes_128_ecb(b, k)
    return e[:bl]


def md_hash_(m, h, bl):
    h_ = h
    for i in range(0, len(m), bl):
        h_ = small_enc(m[i:i + bl], h_, bl)
    return h_


def hash_easy(m, h):
    return md_hash_(m, h, EASY_BLOCK_LEN_BYTES)


def hash_hard(m, h):
    return md_hash_(m, h, HARD_BLOCK_LEN_BYTES)


def test_md_hash():
    n_round = 10
    for x in range(n_round):
        l = random.randrange(1, 99)
        m = os.urandom(l).encode('hex')
        h = hash_easy(m, EASY_KEY)
        print "{m}:{h}".format(m=m, h=str(h).encode('hex'))


def get_random_m():
    l = random.randrange(EASY_BLOCK_LEN_BYTES, 32, EASY_BLOCK_LEN_BYTES)
    m = ''.join(random.choice(ALPHABET) for i in range(l))
    return m


def find_collision(h):
    m0 = get_random_m()
    t0 = hash_easy(m0, h)
    max_try = 2 << 16
    for x in xrange(max_try):
        m1 = get_random_m()
        t1 = hash_easy(m1, h)
        if t1 == t0:
            if m1 == m0:
                continue
            print "\r" + " " * 60 + "\r",
            return [m0, m1]
        if x & 0xff == 0xff:
            print "\rround {x:x} m1={m1};t1={t1}".format(x=x, m1=m1, t1=str(t1).encode('hex')) + ' ' * 20,
            sys.stdout.flush()
    return None


def test_find_collision():
    n_round = 10
    for i in range(n_round):
        ret = find_collision(EASY_KEY)
        if ret is None:
            print "Bad luck, retrying"
            continue
        m0, m1 = ret
        t = hash_easy(m0, EASY_KEY)
        print "Found collision {m0}:{m1}:{t}".format(m0=m0, m1=m1, t=str(t).encode('hex'))
        h0 = hash_easy(m0, EASY_KEY)
        h1 = hash_easy(m1, EASY_KEY)
        assert h0 == h1, 'Wrong collision'


def make_combines(bin_tuples):
    n = len(bin_tuples)
    fmt_str = '0{n}b'.format(n=n)
    for x in range(1 << n):
        m = []
        s = format(x, fmt_str)
        for y in range(n):
            idx = int(s[y])
            m.append(bin_tuples[y][idx])
        yield m


def test_make_combines(n=10):
    bin_tuples = [['1', '0'] for x in range(n)]
    pool = []
    for x in make_combines(bin_tuples):
        pool.append(''.join(x))
    fmt_str = '0{n}b'.format(n=n)
    for x in range(1 << n):
        s = format(x, fmt_str)
        assert s in pool, 'Not found in combinations {s}'.format(s=s)
    print 'Test pass'


def collisions_for_debug():
    return [['4Ku0N1Q7V2', 'XO'],
            ['5uo9TBlOdEff', 'Oh6jCq'],
            ['AHJ2s4', 'NXuj5lEkBdsoqoK9FEEpExIm'],
            ['RMuAZ5gY9z4R7T0OofmSzfNm', 'mKMe66'],
            ['HhrHro39Bm', '5ZA94XSADxPIL5Z2XuewkXhg'],
            ['PghKnn4dDHGRrgfAmUs6CNKyr4', 'nH'],
            ['LQ', 'Snytw1dtFcxHMcRO24m9sDYShX8J'],
            ['S30YGmNHyT3s', '2Gd20tieLvvB7CkiifoX'],
            ['MPwbuQ8vDjNyOfdZ1tAeUAI6riRlUd', 'Nt8H4GDZAs6NKeHvkYE73zmE'],
            ['Gy', '12gXVVzYRZMJmaUKDZq8mo'],
            ['rc0UwRLtfkKMpAQzExSkxLGn', 'piVe8sQ47KZWbwAPCIa7kn'],
            ['TxIWPhUKgFV0BqUFD2TgbHp6Yf', 'nQeIKc'],
            ['hnf4rDmICo4fCpjDVksAVDFd7LAL', '31TrrYJIcr7TkaXt4t'],
            ['gM72Zm', 'fIxXQtpWgV2jAo58WZXl'],
            ['ahNWFKG0KIZ25LSR9YfK', 'LcCDQCjhX9h5hV5Q0XJvJ0ARYphE'],
            ['dpgW', 'RcOKJK8sbuZztihZ8s']]


def find_2n_collision(n):
    collisions = []
    h = EASY_KEY
    while len(collisions) < n:
        r = find_collision(h)
        if r is None:
            print "Bad luck, retrying"
            continue
        m0, m1 = r
        h = hash_easy(m0, h)
        print "Collision found {m0}, {m1}, {h}".format(m0=m0, m1=m1, h=str(h).encode('hex'))
        collisions.append(r)
    return make_combines(collisions)


def test_find_2n_collision(n):
    h = None
    head_c = None
    for t in find_2n_collision(n):
        c = ''.join(t)
        if h is None:
            h = hash_easy(c, EASY_KEY)
            head_c = c
            continue
        h_ = hash_easy(c, EASY_KEY)
        assert h == h_, 'Inequal hash {head_c}, {c}'.format(head_c=head_c, c=c)
    print 'Pass'


def find_collision_in_pool(pool, ps):
    nb = {}
    ctr = 0
    for p in pool:
        m = ''.join(p)
        ctr += 1
        if ctr & 0xff == 0xff:
            print '\rSearching {ctr:x}/{ps:x}'.format(ctr=ctr, ps=ps) + ' ' * 10,
            sys.stdout.flush()
        h = str(hash_hard(m, HARD_KEY))
        if h not in nb:
            nb[h] = [m]
        else:
            nb[h].append(m)
            print "\nFound, {h}:{ms}".format(h=str(h).encode('hex'), ms=nb[h])
    ret = []
    for k, v in nb.items():
        if len(v) > 1:
            ret.append(v)
    return ret


def find_chain_collision():
    easy_collisions = find_2n_collision(HARD_BLOCK_LEN_BYTES * 8 / 2)
    ps = 1 << (HARD_BLOCK_LEN_BYTES * 8 / 2)
    ret = find_collision_in_pool(easy_collisions, ps)
    if len(ret) > 0:
        print "Found harder collision"
        for x in ret:
            h = hash_hard(x[0], HARD_KEY)
            print "hash: {h}".format(h=str(h).encode('hex'))
            for y in x:
                print y
