#!/usr/bin/python

from common.converts import unhex, hamming_distance, b64decode
from xor_cipher_eval import solve

def get_key_distance(cipher, key_size):
    hd = hamming_distance(cipher[0:key_size], cipher[key_size:2*key_size])
    return hd * 1.0 / key_size

def find_key_size(cipher, n):
    hd = [[x, get_key_distance(cipher, x)] for x in range(2, n)]
    hd.sort(key=lambda x: x[1])
    return hd

def find_key(cipher, key_size):
    for ks in range(key_size):
        print "position %d ================" % ks
        blk = cipher[ks::key_size]
        guess = solve([blk])
        import pdb; pdb.set_trace()
        print guess[-3:][:1]

def run():
    with open('set1/6.txt') as f:
        cipher = b64decode(f.read().replace('\n', ''))
    key_guess = find_key_size(cipher, 200)
    # just use the best guess...
    find_key(cipher, key_guess[0][0])

run()
