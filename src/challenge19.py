# Challenge 19

from os import urandom
from converts import b64decode, encrypt_aes_128_ctr, fixed_xor
from xor_cipher_eval import get_alphabet_count, eval_keys, eval_freq, ALPHABET, INVALID_ALPHABET
from misc import static_vars, Singleton
import csv

KEY_SIZE = 16
KEY_B64 = 'TD7obs//l2+PNdTsxg/uRQ=='

def target():
    key = b64decode(KEY_B64)
    with open('19.txt') as f:
        lines = [b64decode(x.strip()) for x in f.readlines()]
        for x in lines:
            print str(x) + "<"
        print "^^^^^^^^^^^^^^^^^^^^^^^"
        print "above is plain"
        ciphers = [encrypt_aes_128_ctr(x, key) for x in lines]
        return ciphers


@static_vars(english_dict=None)
def get_dict():
    if get_dict.english_dict is None:
        get_dict.english_dict = {}
        with open('english_words.csv') as dictfile:
            csvfile = csv.reader(dictfile)
            for line in csvfile:
                get_dict.english_dict[line[1]] = float(line[5])
    return get_dict.english_dict


def solve_byte_xor(cipher):
    keys = bytearray(range(256))
    results = eval_keys([cipher], keys, eval_freq, 1)
    return results


def get_trans_blk(ciphers, idx):
    return bytearray([x[idx] for x in ciphers if len(x) > idx])


class NGramTree(object):
    __metaclass__ = Singleton
    def __init__(self):
        self.levels = {}
        with open('w3.txt') as f:
            probe = []
            csvfile = csv.reader(f, delimiter='\t')
            print "init NGramTree"
            counter = 0
            for line in csvfile:
                self.add(line[1:], int(line[0]))
                counter += 1
                if counter % 10000 == 0:
                    print counter
            print "NGramTree loaded"

    def add(self, path, weight):
        diffroot = self.levels
        for l in range(3):
            probe = diffroot.get(path[l], None)
            if probe is None:
                for r in range(l, 3):
                    diffroot[path[r]] = {}
                    diffroot = diffroot[path[r]]
                diffroot['#'] = weight
                return
            else:
                diffroot = probe

    def check(self, path):
        root = self.levels
        for l in path:
            probe = root.get(l, None)
            if probe is None:
                return 0
            root = probe
        return root['#']

def eval_by_word(plain):
    words = str(plain).strip().split()
    english_dict = get_dict()
    if words[-1] in english_dict:
        return english_dict[words[-1]]
    else:
        return 0

def eval_by_ngram(plain):
    words = str(plain).strip().split()
    if len(words) < 3:
        return 0
    ngtree = NGramTree()
    return ngtree.check(words[-3:])


def solve_byte_context(ciphers, plains, pos):
    guess_plains = []
    for guess_key in range(256):
        score = 0
        presence = 0
        guess_trans = bytearray()
        for idx in range(len(ciphers)):
            if len(ciphers[idx]) <= pos:
                guess_byte = 0
            else:
                presence += 1
                guess_byte = ciphers[idx][pos] ^ guess_key
                if chr(guess_byte) in INVALID_ALPHABET or guess_byte > 127:
                    break
                plain = plains[idx] + bytearray(chr(guess_byte))
                score += eval_by_ngram(plain)
            guess_trans.append(guess_byte)
        if len(guess_trans) < len(ciphers):
            # this indicates we have "breaked" in the for loop
            continue
        non_ab_ratio = 1.0 - get_alphabet_count(guess_trans) * 1.0 / len(
            guess_trans)
        guess_plains.append([
            guess_key, non_ab_ratio, 1.0 - score * 1.0 / presence, guess_trans
        ])
    guess_plains.sort(key=lambda x: x[1:3])
    return guess_plains


def interactive_attack(ciphers, plains, progress):
    blk = get_trans_blk(ciphers, progress)
    blk_guess = solve_byte_xor(blk)
    for i in range(64):
        for j in range(len(ciphers)):
            if len(ciphers[j]) <= progress:
                #print str(plains[j])
                pass
            else:
                c = ciphers[j][progress] ^ blk_guess[i][0]
                if c > 127:
                    print "XXX"
                    break
                print str(plains[j]) + chr(c) + "<"
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        print "above for key={k}".format(k=blk_guess[i][0])


def attack(ciphers):
    # first run, try transposed frequency & hemming distance
    min_len = min([len(x) for x in ciphers])
    key_stream_guess = bytearray()
    for k in range(min_len):
        blk = get_trans_blk(ciphers, k)
        blk_guess = solve_byte_xor(blk)
        key_stream_guess.append(blk_guess[0][0])
    hunch = bytearray([7, 106, 246, 249, 110, 86, 175, 224, 98, 23, 143, 20, 117, 48, 103, 140, 27])
    key_stream_guess += hunch
    plains = []
    for c in ciphers:
        plain = fixed_xor(key_stream_guess, c)
        plains.append(plain)
        #print plain
    print
    print
    print
    print "=========== interactive ==============="
    # uncomment this to start adding hunch
#    interactive_attack(ciphers, plains, len(key_stream_guess))

    final_plains = []
    for c in ciphers:
        plain = fixed_xor(key_stream_guess, c)
        final_plains.append(plain)

    return final_plains


def run():
    ciphers = target()
    plains = attack(ciphers)
    for x in plains:
        print x


run()
