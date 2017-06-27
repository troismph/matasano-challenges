import os
import random
import string
import sys

from converts import pkcs7_pad, encrypt_aes_128_ecb

EASY_BLOCK_LEN_BYTES = 2
HARD_BLOCK_LEN_BYTES = 4
ALPHABET = string.ascii_letters + string.digits


def get_random_m(l=None):
    l = l or random.randrange(EASY_BLOCK_LEN_BYTES, 32, EASY_BLOCK_LEN_BYTES)
    m = ''.join(random.choice(ALPHABET) for i in range(l))
    return m


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
    key = bytearray(os.urandom(EASY_BLOCK_LEN_BYTES))
    n_round = 10
    for x in range(n_round):
        l = random.randrange(1, 99)
        m = os.urandom(l).encode('hex')
        h = hash_easy(m, key)
        print "{m}:{h}".format(m=m, h=str(h).encode('hex'))


def find_collision(h, hash_func):
    m0 = get_random_m()
    t0 = hash_func(m0, h)
    max_try = 2 << 16
    for x in xrange(max_try):
        m1 = get_random_m()
        t1 = hash_func(m1, h)
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
    key = bytearray(os.urandom(EASY_BLOCK_LEN_BYTES))
    n_round = 4
    for i in range(n_round):
        ret = find_collision(key, hash_easy)
        if ret is None:
            print "Bad luck, retrying"
            continue
        m0, m1 = ret
        t = hash_easy(m0, key)
        print "Found collision {m0}:{m1}:{t}".format(m0=m0, m1=m1, t=str(t).encode('hex'))
        h0 = hash_easy(m0, key)
        h1 = hash_easy(m1, key)
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


def incr_block(block, alphabet=None):
    """
    :type block: bytearray 
    :type alphabet: str
    :return: 
    """
    overflow = True
    for idx in range(len(block)):
        if alphabet is None:
            if block[idx] == 0xff:
                continue
            else:
                block[idx] += 1
                overflow = False
                for c in range(idx):
                    block[c] = 0
                break
        else:
            if block[idx] == alphabet[-1]:
                continue
            else:
                next_idx = alphabet.index(chr(block[idx])) + 1
                block[idx] = alphabet[next_idx]
                overflow = False
                for c in range(idx):
                    block[c] = alphabet[0]
                break
    return overflow


def enum_block(bl, alphabet=None):
    """
    An iterator to generae all possible values of one block
    :param bl: block length in bytes
    :type alphabet: bytearray
    :return: 
    """
    ctr = 0
    if alphabet:
        alphabet = bytearray(alphabet)
    blk = bytearray([alphabet[0]] * bl) if alphabet else bytearray(bl)
    yield blk
    while not incr_block(blk, alphabet):
        yield blk
        ctr += 1


def test_enum_block():
    dedup = set()
    n = 2
    for blk in enum_block(n):
        dedup.add(str(blk))
    assert len(dedup) == (1 << (n * 8)), 'Test failed, get:need={g}:{n}'.format(g=len(dedup), n=(1 << (2 * 8)))
    print 'Test pass'
