#!/usr/bin/python

from converts import unhex, hamming_distance, b64decode, xor_cipher
from xor_cipher_eval import solve, cross

def get_key_distance(cipher, key_size):
    distance_sum = 0.0
    r = len(cipher) / key_size
    for i in range(r - 1):
        sec_a = cipher[i * key_size: (i + 1) * key_size]
        sec_b = cipher[(i + 1) * key_size: (i + 2) * key_size]
        distance_sum += hamming_distance(sec_a, sec_b)
    return distance_sum / (r * key_size)

def find_key_size(cipher, n):
    hd = [[x, get_key_distance(cipher, x)] for x in range(2, n)]
    hd.sort(key=lambda x: x[1])
    return hd

def find_key(cipher, key_size):
    key_guess = []
    for ks in range(key_size):
        blk = cipher[ks::key_size]
        blk_guess = solve([blk])
        key_guess.append([x[0] for x in blk_guess])
    return key_guess

def run():
    with open('6.txt') as f:
        cipher = b64decode(f.read().replace('\n', ''))
    key_size = find_key_size(cipher, 40)[0][0]
    guess_idx = [0 for x in range(key_size)]
    # add a few hand-tunes
    guess_idx[15] = 1
    guess_idx[22] = 2
    key_guess = find_key(cipher, key_size)
    key = [key_guess[i][guess_idx[i]] for i in range(key_size)]
    plain = xor_cipher(cipher, bytearray(key))
    # side marks for hand-tuning
    print "01234567890123456789012345678901234567890123456789"
    print plain

run()
