#!/usr/bin/python

from misc import static_vars
from converts import unhex, xor_cipher
import editdistance


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
INVALID_ALPHABET = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f"
KNOWN_FREQ_SEQ = "ETAOINSRHDLUCMFYWGPBVKXQJZ"

def get_chr_freq(s):
    freq = {}
    for c in s:
        if not(chr(c) in ALPHABET):
            continue
        freq[c] = freq.get(c, 0) + 1
    freq_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    freq_seq = map(lambda x: chr(x[0]), freq_items)
    return bytearray(freq_seq)

def get_alphabet_count(plain):
    cnt = sum([1 if chr(x) in ALPHABET else 0 for x in plain])
    return cnt

def get_invalid_alphabet_count(plain):
    cnt = sum([1 if chr(x) in INVALID_ALPHABET or x > 127 else 0 for x in plain])
    return cnt

def get_rel(str_order):
    p = [[str_order[y] + str_order[x] for y in range(x)] for x in range(len(str_order))]
    q = reduce(lambda x, y: x + y, p, [])
    return set(q)

KNOWN_REL = get_rel(KNOWN_FREQ_SEQ)

def eval_order(plain):
    ab_ratio = get_alphabet_count(plain) * 1.0 / len(plain)
    specimen = str(get_chr_freq(plain))
    rel = get_rel(specimen)
    if len(rel) == 0:
        return 1.0
    its = rel & KNOWN_REL
#    print plain, ab_ratio, specimen, len(its), len(rel)
    return 1.0 - len(its) * 1.0 / len(rel)

def eval_freq(plain):
    freq = str(get_chr_freq(plain))
    distance = editdistance.eval(freq, KNOWN_FREQ_SEQ)
#    print plain, freq, KNOWN_FREQ_SEQ[:len(freq)], distance
    return distance

@static_vars(dictionary=None)
def eval_dict(plain):
    if eval_dict.dictionary is None:
        with open('set1/dictionary.txt') as f:
            eval_dict.dictionary = set([x.rstrip() for x in f])
    words = str(plain).split()
    if len(words) <= 1:
        return 100
    word_len = reduce(lambda x, y: x + y, map(lambda x: len(x) if x in eval_dict.dictionary else 0, words))
    return 100 - word_len * 100.0 / len(plain)

def eval_keys(arr_cipher, arr_keys, eval_func, inv_thres=0):
    eval_items = []
    for cipher in arr_cipher:
        for key in arr_keys:
            plain = xor_cipher(cipher, bytearray([key])).upper()
            inv_ratio = get_invalid_alphabet_count(plain) * 1.0 / len(plain)
            if inv_ratio > inv_thres:
                continue
            ab_ratio = get_alphabet_count(plain) * 1.0 / len(plain)
            score = eval_func(plain)
            eval_items.append([key, 1.0 - ab_ratio, score, plain, cipher])
    eval_items.sort(key=lambda x: x[1:3])
    #eval_items.sort(key=lambda x:[x[2], x[1]])
    return eval_items

def solve(cipher):
    keys = bytearray(range(128))
    results = eval_keys(cipher, keys, eval_freq)
    return results

def cross(vectors):
    if len(vectors) == 0:
        return []
    if len(vectors) == 1:
        return [[x] for x in vectors[0]]
    ret = []
    ri = cross(vectors[:-1])
    for v in vectors[-1]:
        for x in ri:
            ret.append(x + [v])
    return ret

