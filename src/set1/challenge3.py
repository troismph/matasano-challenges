#!/usr/bin/python

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

def filter_freq(s):
    ret = ""
    for x in s:
        if x.isalpha():
            ret = ret + x.upper()
    return ret

def solve(cipherhex):
    cipher = unhex(cipherhex)
    try_items = []
    chr_freq = get_chr_freq(cipher)
    freq_len = len(chr_freq)
    for key in range(128):
        try_plain = xor_cipher(cipher, bytearray([key]))
        try_freq = str(xor_cipher(chr_freq, bytearray([key]))).upper()
        distance = editdistance.eval(try_freq, KNOWN_FREQ_SEQ[:freq_len])
        try_items.append([key, distance, try_plain, try_freq])
    try_items.sort(key=lambda x: x[1], reverse=True)
    for x in try_items:
        print x[0], x[1], x[2], x[3]

solve("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")
