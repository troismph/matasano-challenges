# A naive RSA implementation
import os
import random
import gensafeprime
from converts import bin_str_to_big_int, big_int_to_bin_str
from math_g4z3 import mod_exp
from math_g4z3 import gcd, inv_mod


PRIME_LEN_BYTES = 4
PRIME_LEN_BITS = PRIME_LEN_BYTES * 8
BLOCK_LEN_BYTES = PRIME_LEN_BYTES * 2


def gen_prime(bits):
    return gensafeprime.generate(bits)


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
