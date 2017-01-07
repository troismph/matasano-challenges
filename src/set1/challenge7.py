#!/usr/bin/python

import cffi
from common.converts import b64decode


class CFFIEnvType:
    def __init__(self):
        with open("set1/challenge7.h") as f:
            header_code = f.read()
        with open("set1/challenge7.c") as f:
            impl_code = f.read()
        self.FFI = cffi.FFI()
        self.FFI.cdef(header_code)
        self.C = self.FFI.verify(impl_code, libraries=["crypto"])


CFFIEnv = CFFIEnvType()

def decrypt_aes_128_ecb(cipher, key):
    # we handle only bytearrays!
    cipher_len = len(cipher)
    plain_len = cipher_len + 128
    plain = CFFIEnv.FFI.new("char[%s]" % (plain_len))
    n = CFFIEnv.C.decrypt_aes_128_ecb(cipher, cipher_len, plain, plain_len, key)
    print "%d bytes decrypted" % n
    return CFFIEnv.FFI.string(plain, n)

def run():
    with open("set1/7.txt") as f:
        cipher = str(b64decode(f.read().replace('\n', '')))
    key = "YELLOW SUBMARINE"
    plain = decrypt_aes_128_ecb(cipher, key)
    print plain

run()
