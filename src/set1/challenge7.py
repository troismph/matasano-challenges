#!/usr/bin/python

import cffi


def prep_cffi():
    _FFI = cffi.FFI()
    _FFI.cdef("""
    int decrypt_aes_128_ecb(unsigned char* cipher,
        unsigned char* key, unsigned char* plain,
        unsigned int plainlen);
    int encrypt_aes_128_ecb(unsigned char* cipher,
        unsigned char* key, unsigned char* plain,
        unsigned int cipherlen);""")
    _C = _FFI.verify("""
    #include <openssl/evp.h>

    int decrypt_aes_128_ecb(unsigned char* cipher,
        unsigned char* key, unsigned char* plain,
        unsigned int plainlen) {
        EVP_CIPHER_CTX ctx;

    }

""")

def decrypt_aes_128_ecb(cipher, key):
    # we handle only bytearrays!
    pass



def run():
    _FFI = cffi.FFI()
    _FFI.cdef("""
    int call_me(int a, int b);""")
    _C = _FFI.verify("""
    int call_me(int a, int b){
        int c = a + b;
        return c;
    }""")
    r = _C.call_me(99, 99)
    print r

run()
