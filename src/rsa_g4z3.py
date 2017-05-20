# A naive RSA implementation
import os
import sys
import random
import gensafeprime
from converts import bin_str_to_big_int, big_int_to_bin_str, sha256, pkcs15_pad, pkcs15_unpad
from math_g4z3 import mod_exp
from math_g4z3 import gcd, inv_mod


def gen_prime(bits):
    return gensafeprime.generate(bits)


def get_p_q(len_bits):
    p = gen_prime(len_bits)
    q = p
    cnt = 0
    while q == p and cnt < 30:
        q = gen_prime(len_bits)
        cnt += 1
    assert q != p, "Prime pair generation failed"
    return p, q


def get_totient(p, q):
    return (p - 1) * (q - 1)


def get_e(t):
    e = random.randrange(2, t)
    while gcd(e, t) != 1:
        e = random.randrange(2, t)
    return e


def rsa_gen_key(**kwargs):
    """
    :return: [0]: public key, [1]: private key
    """
    block_len_bits = kwargs.get("len", 256)
    prime_len_bits = block_len_bits / 2
    p, q = get_p_q(prime_len_bits)
    n = p * q
    t = get_totient(p, q)
    e = kwargs.get("e", get_e(t))
    d = inv_mod(e, t)
    return [e, n, block_len_bits], [d, n, block_len_bits]


def rsa_encrypt(in_buf, key):
    out_blocks = []
    block_len_bytes = key[2] >> 3
    for h in range(0, len(in_buf), block_len_bytes):
        m = bin_str_to_big_int(str(in_buf[h:h + block_len_bytes]))
        c = mod_exp(m, key[0], key[1])
        out_blocks.append(big_int_to_bin_str(c, block_len_bytes))
    return "".join(out_blocks)


def rsa_decrypt(in_buf, key, pad=False):
    out_blocks = []
    block_len_bytes = key[2] >> 3
    for h in range(0, len(in_buf), block_len_bytes):
        c = bin_str_to_big_int(str(in_buf[h:h + block_len_bytes]))
        m = mod_exp(c, key[0], key[1])
        cand = big_int_to_bin_str(m)
        if pad:
            l_z = '\x00' * (block_len_bytes - len(cand))
            out_blocks.append(l_z + cand)
        else:
            out_blocks.append(cand)
    return "".join(out_blocks)


def test_rsa():
    n_round = 10
    print "Generating 1024 bit rsa key pair...",
    sys.stdout.flush()
    pk, sk = rsa_gen_key(len=1024)
    print "OK, testing..."
    for x in range(n_round):
        print "\rRound {n}".format(n=x),
        sys.stdout.flush()
        l = random.randrange(7, 2099)
        msg = os.urandom(l).encode('hex')
        cipher = rsa_encrypt(msg, pk)
        plain = rsa_decrypt(cipher, sk)
        assert plain == msg, "Decryption corrupted"
    print "\rTest pass after {n} rounds".format(n=n_round)


def rsa_sign(msg, sk):
    block_len_bytes = sk[2] >> 3
    digest = sha256(msg)
    block = pkcs15_pad(digest, block_len_bytes)
    cipher = rsa_encrypt(block, sk)
    return cipher


def rsa_validate(msg, sig, pk, bug=False):
    block = rsa_decrypt(sig, pk, True)
    remote_digest = pkcs15_unpad(block, bug)
    digest = sha256(msg)
    return digest == remote_digest


def test_rsa_sign():
    block_len_bits = 1024
    n_round = 10
    for x in range(n_round):
        print "\r" + " " * 100,
        print "\rRound {n}. Generating {l} bits rsa key pair...".format(n=x, l=block_len_bits),
        sys.stdout.flush()
        pk, sk = rsa_gen_key(len=block_len_bits, e=3)
        msg = os.urandom(random.randrange(2, 3000)).encode('hex')
        print "Creating signature",
        sys.stdout.flush()
        sig = rsa_sign(msg, sk)
        print ", Validating",
        sys.stdout.flush()
        assert rsa_validate(msg, sig, pk), "Validation fail"
        print "...OK",
    print "\r" + " " * 100,
    print "\rTest pass after {n} rounds".format(n=n_round)
