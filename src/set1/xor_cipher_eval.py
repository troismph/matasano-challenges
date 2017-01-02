#!/usr/bin/python

from common.misc import static_vars
from common.converts import unhex, xor_cipher
import editdistance


KNOWN_FREQ_SEQ = "ETAOINSRHDLUCMFYWGPBVKXQJZ"

def get_chr_freq(s):
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    freq_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    freq_seq = map(lambda x: chr(x[0]), freq_items)
    return bytearray(freq_seq)

def eval_keys(arr_cipherhex, arr_keys, eval_func):
    eval_items = []
    for cipherhex in arr_cipherhex:
        cipher = unhex(cipherhex)
        for key in arr_keys:
            plain = xor_cipher(cipher, bytearray([key])).upper()
            score = eval_func(plain)
            eval_items.append([key, score, plain, cipherhex])
    eval_items.sort(key=lambda x: x[1], reverse=True)
    return eval_items

def eval_freq(plain):
    freq = str(get_chr_freq(plain))
    distance = editdistance.eval(freq, KNOWN_FREQ_SEQ[:len(freq)])
    print plain, freq, KNOWN_FREQ_SEQ[:len(freq)], distance
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

def solve(cipherhex):
    keys = bytearray(range(128))
    results = eval_keys(cipherhex, keys, eval_freq)
    return results
