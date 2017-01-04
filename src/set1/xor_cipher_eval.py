#!/usr/bin/python

from common.misc import static_vars
from common.converts import unhex, xor_cipher
import editdistance


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
KNOWN_FREQ_SEQ = "ETAOINSRHDLUCMFYWGPBVKXQJZ"

@static_vars(alphabet=None)
def in_alphabet(c):
    if in_alphabet.alphabet is None:
        in_alphabet.alphabet = set([ord(x) for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"])
    return c in in_alphabet.alphabet

def get_chr_freq(s):
    freq = {}
    for c in s:
        if not in_alphabet(c):
            continue
        freq[c] = freq.get(c, 0) + 1
    freq_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    freq_seq = map(lambda x: chr(x[0]), freq_items)
    return bytearray(freq_seq)

def eval_keys(arr_cipher, arr_keys, eval_func):
    eval_items = []
    for cipher in arr_cipher:
        for key in arr_keys:
            plain = xor_cipher(cipher, bytearray([key])).upper()
            ab_ratio = get_alphabet_count(plain) * 1.0 / len(plain)
            score = eval_func(plain)
            eval_items.append([key, 1.0 - ab_ratio, score, plain, cipher])
    eval_items.sort(key=lambda x: x[1:3], reverse=True)
    return eval_items

def get_alphabet_count(plain):
    cnt = sum([1 if str(x) in ALPHABET else 0 for x in plain])
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
    words = str(plain).split(' ')
    if len(words) <= 1:
        return 100
    word_len = reduce(lambda x, y: x + y, map(lambda x: len(x) if x in eval_dict.dictionary else 0, words))
    return 100 - word_len * 100.0 / len(plain)

def solve(cipher):
    keys = bytearray(range(128))
    results = eval_keys(cipher, keys, eval_order)
    return results
