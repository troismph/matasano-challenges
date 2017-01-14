#!/bin/python

import string, random
from converts import encrypt_aes_128_ecb, encrypt_aes_128_cbc


def rand_str(str_len):
    return "".join(random.choice(string.ascii_letters + string.digits) for x in range(str_len))

def rand_bytes(key_len):
    return bytearray(random.randint(0, 255) for x in range(key_len))

def enc_oracle(in_buf_intact):
    # God doesn't play dice, but orcales do!
    key_len = 16
    # Random prefix and suffix
    prfx = rand_str(random.randint(5, 10))
    sfx = rand_str(random.randint(5, 10))
    in_buf = prfx + in_buf_intact + sfx
    key = rand_bytes(key_len)
    if random.choice([True, False]):
        cipher = encrypt_aes_128_ecb(in_buf, key)
        tag = "ecb"
    else:
        iv = rand_bytes(key_len)
        cipher = encrypt_aes_128_cbc(in_buf, key, iv)
        tag = "cbc"
    return cipher, tag

def eval_dup(buf):
    key_len = 16
    stat = {}
    s = str(buf)
    chips = [s[x : x + key_len] for x in range(0, len(s), key_len)]
    for c in chips:
        stat[c] = stat.get(c, 0) + 1
    return stat

def detect_stat(stat):
    ret = {}
    for key, val in stat.items():
        if val > 1:
            ret[key] = val
    return ret

def speculator(oracle_func):
    key_len = 16
    q = bytearray(65 for x in range(key_len * 4))
    cipher, tag = oracle_func(q)
    stat = eval_dup(cipher)
    evidence = detect_stat(stat)
    if len(evidence) > 0:
        guess = "ecb"
    else:
        guess = "cbc"
    print "{0}: guess vs. fact = {1} vs. {2}".format("Y" if guess == tag else "N", guess, tag)

def run():
    for x in xrange(20):
        speculator(enc_oracle)

run()

