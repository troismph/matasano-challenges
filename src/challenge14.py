#!/bin/python
# Too lazy to refactor w/ challenge12 code, just  copy...

from converts import encrypt_aes_128_ecb, b64decode
from misc import static_vars
from os import urandom
import random


SECRET = b64decode("Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK")

@static_vars(key=None, prefix=None)
def enc_oracle(buf_intact):
    key_len = 16
    if enc_oracle.key is None:
        enc_oracle.key = bytearray(urandom(key_len))
    if enc_oracle.prefix is None:
        enc_oracle.prefix = bytearray(urandom(random.randint(1, 64)))
        #print "prefix len {pl}".format(pl=len(enc_oracle.prefix))
    plain = enc_oracle.prefix + buf_intact + SECRET
    return encrypt_aes_128_ecb(plain, enc_oracle.key)

def get_mark(oracle_func, padding):
    key_len = 16
    blk_cnt = 4
    test_buf = bytearray([padding for x in range(key_len * blk_cnt)])
    c = str(oracle_func(test_buf))
    stat = {}
    chips = [c[x : x + key_len] for x in range(0, len(c), key_len)]
    for c in chips:
        stat[c] = stat.get(c, 0) + 1
    for key, val in stat.items():
        if val > 1:
            return key

def find_common_prefix(buf_a, buf_b, key_len):
    for x in range(0, min(len(buf_a), len(buf_b)), key_len):
        if buf_a[x : x + key_len] == buf_b[x : x + key_len]:
            continue
        return x / key_len

def find_prefix_len(oracle_func, key_len):
    prev_cipher = None
    cps = []
    for x in range(key_len + 1):
        hack_input = bytearray(['H' for i in range(x)])
        cur_cipher = oracle_func(hack_input)
        if prev_cipher is not None:
            cps.append(find_common_prefix(prev_cipher, cur_cipher, key_len))
        else:
            cps.append(None)
        prev_cipher = cur_cipher
    #print cps
    for x in range(1, len(cps) - 1):
        if cps[x] < cps[x + 1]:
            #print cps[x], x, cps[x] * key_len + key_len -x
            return cps[x] * key_len + key_len - x
    return cps[1] * key_len

def get_key_len(oracle_func):
    plain = bytearray()
    prev_len = 0
    for try_len in xrange(1, 256):
        plain = plain + "A"
        cipher = oracle_func(plain)
        if prev_len == 0:
            prev_len = len(cipher)
            continue
        d = len(cipher) - prev_len
        if d > 0:
            return d

def is_ecb(oracle_func, key_len):
    q = bytearray(65 for x in range(key_len * 4))
    cipher = oracle_func(q)
    stat = {}
    s = str(cipher)
    chips = [s[x : x + key_len] for x in range(0, len(s), key_len)]
    for c in chips:
        stat[c] = stat.get(c, 0) + 1
    for key, val in stat.items():
        if val > 1:
            return True
    return False

class ECBOracleAttacker:
    def __init__(self, key_len, oracle):
        self.key_len = key_len
        self.oracle_prefix_len = find_prefix_len(oracle, key_len)
        self._original_oracle = oracle
        self.shifts = self.prep_shifts()
        cipher = self.oracle("")
        self.s_blk = len(cipher) / self.key_len
        self.guess = bytearray()

    def oracle(self, buf_intact):
        padding_len = (self.key_len - self.oracle_prefix_len % self.key_len) % self.key_len
        padded_prefix_len = self.oracle_prefix_len + padding_len
        padding = bytearray(['H' for x in range(padding_len)])
        c = self._original_oracle(padding + buf_intact)
        del c[:padded_prefix_len]
        return c

    def prep_shifts(self):
        shifts = []
        for x in range(self.key_len):
            if x == 0:
                prefix = bytearray()
            else:
                prefix = bytearray().join(["A" for i in range(self.key_len - x)])
            shifts.append(self.oracle(prefix))
        return shifts

    def solve_byte(self, shift_n, block_n):
        blk = self.get_block(shift_n, block_n)
        known = self.get_known(shift_n, block_n)
        known.extend(chr(0))
        for x in xrange(256):
            known[-1] = x
            cipher = self.oracle(known)
            if blk == cipher[:self.key_len]:
                return x
        return -1

    def solve(self):
        shift_order = range(1, self.key_len + 1)
        for b in range(self.s_blk):
            for s in shift_order:
                g = self.solve_byte(s, b)
                if g < 0:
                    return
                self.guess.extend(chr(g))

    def pos_trans(self, shift_n, block_n):
        pass

    def get_known(self, shift_n, block_n):
        g_pos = block_n * self.key_len + shift_n - 1
        blk_low = g_pos - self.key_len + 1
        known_blk = [chr(self.guess[x]) if x >= 0 else "A" for x in range(blk_low, g_pos)]
        return bytearray().join(known_blk)

    def get_block(self, shift_n, block_n):
        blk_low = block_n * self.key_len
        return self.shifts[shift_n % self.key_len][blk_low : blk_low + self.key_len]


def run():
    key_len = get_key_len(enc_oracle)
    print is_ecb(enc_oracle, key_len)
    attacker = ECBOracleAttacker(key_len, enc_oracle)
    attacker.solve()
    print attacker.guess

