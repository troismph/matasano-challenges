#!/bin/python

import urllib, urlparse
from converts import encrypt_aes_128_cbc, decrypt_aes_128_cbc
import os


KEY_LEN = 16
KEY = bytearray(os.urandom(KEY_LEN))
PREFIX = "comment1=cooking%20MCs;userdata="
POSTFIX = ";comment2=%20like%20a%20pound%20of%20bacon"

def oracle(usr_dat):
    plain = bytearray(PREFIX + urllib.quote(usr_dat) + POSTFIX)
    cipher = encrypt_aes_128_cbc(plain, KEY)
    return cipher

def target(cipher):
    plain = str(decrypt_aes_128_cbc(cipher, KEY))
    qs = urlparse.parse_qs(plain)
    if 'true' in qs.get('admin', []):
        return True, plain
    else:
        return False, plain

def crack():
    hack_str = ";xadm=truex;"
    post_pad_len = (KEY_LEN - len(urllib.quote(hack_str)) % KEY_LEN) % KEY_LEN
    post_pad = "P" * post_pad_len
    usr_dat = "X" * KEY_LEN + ";xadm=truex;" + post_pad
    cipher = oracle(usr_dat)
    hacked, plain = target(cipher)
    print "Normal: {p}".format(p=plain)
    err_mask = bytearray(KEY_LEN)
    err_mask[3] = ord('x') ^ ord(';')
    err_mask[7] = ord('%') ^ ord('i')
    err_mask[8] = ord('3') ^ ord('n')
    err_mask[9] = ord('D') ^ ord('=')
    err_mask[14] = ord('x') ^ ord(';')
    prefix_len = len(PREFIX)
    for i in range(KEY_LEN):
        cipher[prefix_len + i] = cipher[prefix_len + i] ^ err_mask[i]
    hacked, plain = target(cipher)
    print "Hacked: {p}".format(p=plain)

crack()

