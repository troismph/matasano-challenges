#!/usr/bin/python

from common.converts import unhex, hamming_distance, b64decode


def get_key_distance(cipher, key_size):
    hd = hamming_distance(cipher[0:key_size], cipher[key_size:2*key_size])
    return hd * 1.0 / key_size

def find_key_size(cipher, n):
    hd = [[x, get_key_distance(cipher, x)] for x in range(2, n)]
    hd.sort(key=lambda x: x[1])
    print hd

def run():
    with open('set1/6.txt') as f:
        cipher = b64decode(f.read().replace('\n', ''))
    find_key_size(cipher, 100)

run()
