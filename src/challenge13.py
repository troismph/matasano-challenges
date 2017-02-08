#!/usr/bin/python

import urllib, urlparse
from converts import encrypt_aes_128_ecb, decrypt_aes_128_ecb
from os import urandom


def encode_qs(kvs):
    # lazy solution using py's standard lib...
    return urllib.urlencode(kvs)

def decode_qs(s):
    kvs = dict(urlparse.parse_qsl(s))
    return kvs

def profile_for(addr):
    return "email={}&uid=10&role=user".format(addr)

def encrypt_profile_for(addr, key):
    qs = profile_for(addr)
    return encrypt_aes_128_ecb(qs, key)

def decrypt_profile(cipher, key):
    return decrypt_aes_128_ecb(cipher, key)

def attack():
    oracle = encrypt_profile_for
    key = bytearray(urandom(16))
    q0 = "HHHHHHHHHHadmin\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b@bar.com"
    c0 = oracle(q0, key)
    admin_cipher = c0[16:32]
    q1 = "1234567@a.com"
    c1 = oracle(q1, key)
    h = c1[:32] + admin_cipher
    qh = decrypt_profile(h, key)
    print "admin role for 1234567@q.com: " + qh

attack()

