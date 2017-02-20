# Solution for challenge 17
import os
import random
from converts import encrypt_aes_128_cbc, decrypt_aes_128_cbc, pkcs7_unpad, b64decode
from misc import ListSlice

KEY_LEN = 16


class Target:
    def __init__(self):
        with open("17.txt") as f:
            self.lines = [bytearray(x.rstrip()) for x in f.readlines()]
        self.key = os.urandom(KEY_LEN)
        self.iv = bytearray(KEY_LEN)

    def enc_msg(self, idx=None):
        #plain = random.choice(self.lines)
        if idx is None:
            plain = random.choice(self.lines)
        else:
            plain = self.lines[idx]
        cipher = encrypt_aes_128_cbc(plain, self.key, iv=self.iv)
        return cipher, self.iv

    def validate(self, cipher):
        plain = decrypt_aes_128_cbc(cipher, self.key, iv=self.iv, unpad=False)
        try:
            plain_unpad = bytearray()
            plain_unpad[:] = plain
            pkcs7_unpad(plain, KEY_LEN)
            return True, plain_unpad
        except ValueError as e:
            return False, plain


class Attacker:
    def __init__(self, target):
        self.target = target

    def crack_tail_block(self, cipher):
        cipher_len = len(cipher)
        cipher_tmp = cipher[:]
        op_byte = ListSlice(cipher_tmp, cipher_len - 2 * KEY_LEN, KEY_LEN)
        tgt_byte = ListSlice(cipher_tmp, cipher_len - KEY_LEN, KEY_LEN)
        op_byte_orig = ListSlice(cipher, cipher_len - 2 * KEY_LEN, KEY_LEN)
        tgt_byte_orig = ListSlice(cipher, cipher_len - KEY_LEN, KEY_LEN)
        known = bytearray(KEY_LEN)
        mask = bytearray(KEY_LEN)
        for c in range(KEY_LEN - 1, -1, -1):
            for f in range(c + 1, KEY_LEN):
                op_byte[f] = op_byte_orig[f] ^ mask[f] ^ (KEY_LEN - f) ^ (
                    KEY_LEN - c)
            found = False
            for x in range(1, 256):
                op_byte[c] = op_byte_orig[c] ^ x
                valid, plain = self.target.validate(cipher_tmp)
                if valid:
                    mask[c] = x
                    known[c] = x ^ (KEY_LEN - c)
                    found = True
                    break
            if not found:
                mask[c] = 0
                known[c] = KEY_LEN - c
        return known


def run_once(target, idx=None):
    attacker = Attacker(target)
    cipher_orig, iv = target.enc_msg(idx)
    cipher_orig = iv + cipher_orig
    n_block = len(cipher_orig) / KEY_LEN
    decrypted = bytearray()
    for x in range(0, n_block - 1):
        cipher_slice = cipher_orig[x * KEY_LEN:(x + 2) * KEY_LEN]
        known_slice = attacker.crack_tail_block(cipher_slice)
        decrypted += known_slice
    pkcs7_unpad(decrypted, KEY_LEN)
    return decrypted


def run():
    target = Target()
    plain_texts = []
    for x in range(10):
        decrypted = run_once(target, x)
        if decrypted == target.lines[x]:
            print "Pass for index {i}".format(i=x)
            plain_texts.append(b64decode(str(decrypted)))
        else:
            print "Failed for index {i}".format(i=x)
    for x in plain_texts:
        print x


run()
