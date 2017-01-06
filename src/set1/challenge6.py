#!/usr/bin/python

from common.converts import unhex, hamming_distance, b64decode
from xor_cipher_eval import solve, cross

def get_key_distance(cipher, key_size):
    distance_sum = 0.0
    r = len(cipher) / key_size
    print "cipher %d key %d section %d" % (len(cipher), key_size, r)
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
    print
    print
    print "KEY SIZE %d +++++++++++++++" % key_size
    key_guess = []
    for ks in range(key_size):
        print "position %d ================" % ks
        blk = cipher[ks::key_size]
        blk_guess = solve([blk])
        key_guess.append([x[0] for x in blk_guess])
        order = 0
        for g in blk_guess[:5]:
            print "order %d" % order
            order += 1
            print "key %d non-ab %f score %f" % (g[0], g[1], g[2])
            print "plain:" + str(g[3])
    return key_guess

def run():
    with open('set1/6.txt') as f:
        cipher = b64decode(f.read().replace('\n', ''))
#    key_guess = find_key_size(cipher, 40)
#    import pdb; pdb.set_trace()
    # try top n guesses...
    key_guess = find_key(cipher, 29)
    print key_guess
    cnt = reduce(lambda x, y: x * y, [len(x) for x in key_guess])
    print cnt
    #key_space = cross(key_guess)
    #print len(key_space)

def run2():
    with open('set1/6.txt') as f:
        cipher = b64decode(f.read().replace('\n', ''))
    hd = find_key_size(cipher, 40)
    for x in hd:
        print "%d:%f" % (x[0], x[1])
        
run()
