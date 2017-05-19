# A naive RSA implementation
import random
from converts import bin_str_to_big_int, big_int_to_bin_str, pkcs7_pad, pkcs7_unpad
from utils import mod_exp, mod_mult, mod_add
import gensafeprime
import os

PRIME_LEN_BYTES = 4
PRIME_LEN_BITS = PRIME_LEN_BYTES * 8
BLOCK_LEN_BYTES = PRIME_LEN_BYTES * 2


def gen_prime(bits):
    return gensafeprime.generate(bits)


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def egcd(a, b):
    rpp = a
    rp = b
    spp = 1
    sp = 0
    tpp = 0
    tp = 1
    while rp != 0:
        q = rpp / rp
        rpp, rp = rp, rpp % rp
        spp, sp = sp, spp - q * sp
        tpp, tp = tp, tpp - q * tp
    return rpp, spp, tpp


def test_egcd():
    cases = [[18, 27], [18, 7]]
    for case in cases:
        r, s, t = egcd(case[0], case[1])
        assert case[0] * s + case[1] * t == r, "Bezout equation unsatisfied"
        print "{a}*{s} + {b}*{t}=gcd({a}, {b})={r}".format(a=case[0], b=case[1], s=s, t=t, r=r)
        g = gcd(case[0], case[1])
        assert r == g, "GCD mutual verification failed, get {r}, should {g}".format(r=r, g=g)
    print "Test pass"


def inv_mod(e, m):
    """
    Must have that gcd(e, m) = 1
    :param e: 
    :param m: 
    :return: 
    """
    r, s, t = egcd(e, m)
    assert r == 1, "Non-coprime inputs {e}, {m}, gcd={r}".format(e=e, m=m, r=r)
    return s % m


def test_inv_mod():
    cases = [[17, 3120]]
    for case in cases:
        im = inv_mod(case[0], case[1])
        print "{im}*{e} % {m} = 1".format(im=im, e=case[0], m=case[1])
        assert (im * case[0]) % case[1] == 1, "Non-inverse detected"
        assert 0 <= im < case[1], "Out of range"
    print "Test pass"


def get_p_q():
    p = gen_prime(PRIME_LEN_BITS)
    q = p
    while q == p:
        q = gen_prime(PRIME_LEN_BITS)
    return p, q


def get_totient(p, q):
    return (p - 1) * (q - 1)


def get_e(t):
    e = random.randrange(2, t)
    while gcd(e, t) != 1:
        e = random.randrange(2, t)
    return e


def rsa_gen_key(custom_e=None):
    """
    
    :return: [0]: public key, [1]: private key
    """
    p, q = get_p_q()
    n = p * q
    t = get_totient(p, q)
    e = get_e(t) if custom_e is None else custom_e
    d = inv_mod(e, t)
    return [e, n], [d, n]


def rsa_encrypt(in_buf, key):
    out_blocks = []
    for h in range(0, len(in_buf), BLOCK_LEN_BYTES):
        m = bin_str_to_big_int(str(in_buf[h:h + BLOCK_LEN_BYTES]))
        c = mod_exp(m, key[0], key[1])
        out_blocks.append(big_int_to_bin_str(c, BLOCK_LEN_BYTES))
    return "".join(out_blocks)


def rsa_decrypt(in_buf, key):
    out_blocks = []
    for h in range(0, len(in_buf), BLOCK_LEN_BYTES):
        c = bin_str_to_big_int(str(in_buf[h:h + BLOCK_LEN_BYTES]))
        m = mod_exp(c, key[0], key[1])
        out_blocks.append(big_int_to_bin_str(m))
    return "".join(out_blocks)


def test_rsa():
    n_round = 10
    pk, sk = rsa_gen_key()
    for x in range(n_round):
        l = random.randrange(7, 2099)
        msg = os.urandom(l).encode('hex')
        cipher = rsa_encrypt(msg, pk)
        plain = rsa_decrypt(cipher, sk)
        assert plain == msg, "Decryption corrupted"
    print "Test pass after {n} rounds".format(n=n_round)
