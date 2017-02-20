#!/usr/bin/python
import cffi
from misc import static_vars, Singleton
import struct

KEY_LEN = 16

def unhex(s):
    def unhex_byte(ss):
        # ss must be a string
        v = 0
        for i in range(len(ss)):
            if ss[i] >= '0' and ss[i] <= '9':
                v = (v << 4) + ord(ss[i]) - ord('0')
            elif ss[i] >= 'a' and ss[i] <= 'f':
                v = (v << 4) + ord(ss[i]) - ord('a') + 10
            elif ss[i] >= 'A' and ss[i] <= 'F':
                v = (v << 4) + ord(ss[i]) - ord('A') + 10
            else:
                raise ValueError(ss)
        return v

    def unhex_bytes_it(ss):
        assert(len(ss) % 2 == 0)
        chips = [s[x - 2 if x - 2 > 0 else None : x] \
                 for x in range(len(ss), 0, -2)]
        for chip in reversed(chips):
            v = unhex_byte(chip)
            yield v

    r = bytearray(unhex_bytes_it(s))
    return r

B64_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

def b64encode(s):
    npad = (3 - len(s) % 3) % 3
    s = s + bytearray([0 for x in range(npad)])

    sout = ''
    for i in range(0, len(s), 3):
        sout = sout + B64_ALPHABET[(s[i] & 0xfc) >> 2]
        sout = sout + B64_ALPHABET[((s[i] & 0x03) << 4) + (s[i + 1] >> 4)]
        c = ((s[i + 1] & 0x0f) << 2) + ((s[i + 2] & 0xc0) >> 6)
        d = s[i + 2] & 0x3f
        if i + 3 == len(s):
            if npad == 2:
                c = c if c else -1
                d = d if d else -1
            elif npad == 1:
                d = d if d else -1
        sout = sout + B64_ALPHABET[c] + B64_ALPHABET[d]
    return sout

def b64decode(s):
    # s must be a string
    assert(len(s) % 4 == 0)
    def decode_char(c):
        # c must be int
        if c == ord('+'):
            return 62
        elif c == ord('/'):
            return 63
        elif c == ord('='):
            return 0
        elif c - ord('0') < 10:
            return c - ord('0') + 52
        elif c - ord('A') < 26:
            return c - ord('A')
        elif c - ord('a') < 26:
            return c - ord('a') + 26
        else:
            assert(False)

    def decode_quartet(q):
        # q must be string
        assert(len(q) == 4)
        s = bytearray(3)
        t = [decode_char(ord(x)) for x in q]
        s[0] = (t[0] << 2) + ((t[1] & 0x30) >> 4)
        s[1] = ((t[1] & 0x0f) << 4) + ((t[2] & 0x3c) >> 2)
        s[2] = ((t[2] & 0x03) << 6) + t[3]
        npad = q.count('=')
        return s[:-npad if npad else None]

    triples = [decode_quartet(s[i : i + 4]) for i in range(0, len(s), 4)]
    return bytearray().join(triples)

def fixed_xor(buffer_a, buffer_b):
    l = min(len(buffer_a), len(buffer_b))
    buffer_c = bytearray(l)
    for i in range(l):
        buffer_c[i] = buffer_a[i] ^ buffer_b[i]
    return buffer_c

def xor_cipher(plain, key):
    keylen = len(key)
    chips = (plain[i: i + keylen] for i in range(0, len(plain), keylen))
    return reduce(lambda x, y: x + y, map(lambda x: fixed_xor(x, key), chips))

def hamming_distance(buffer_a, buffer_b):
    assert(len(buffer_a) == len(buffer_b))
    byte_cnt = lambda x: bin(x[0] ^ x[1]).count("1")
    return reduce(lambda x, y: x + y, map(byte_cnt, zip(buffer_a, buffer_b)))

def pkcs7_pad(buf, block_len):
    delta = block_len - (len(buf) % block_len)
    if delta == 0:
        delta = block_len
    buf.extend(bytearray([delta for x in range(delta)]))

def pkcs7_unpad(buf, block_len):
    pad_len = buf[-1] if buf[-1] != 0 else block_len
    # validate padding
    for x in buf[-pad_len:]:
        if x != buf[-1]:
            raise ValueError("Bad padding")
    del buf[-pad_len:]

class OpenSSLCFFI(object):
    __metaclass__ = Singleton
    def __init__(self):
        with open("openssl_call.h") as f:
            header_code = f.read()
        with open("openssl_call.c") as f:
            impl_code = f.read()
        self.FFI = cffi.FFI()
        self.FFI.cdef(header_code)
        self.C = self.FFI.verify(impl_code, libraries=["crypto"])

def decrypt_aes_128_ecb(in_buf, key):
    # we handle only bytearrays
    cffienv = OpenSSLCFFI()
    in_len = len(in_buf)
    out_len = in_len + 128
    out_buf = cffienv.FFI.new("unsigned char[]", out_len)
    in_buf_s = str(in_buf)
    key_s = str(key)
    n = cffienv.C.decrypt_aes_128_ecb(in_buf_s, in_len, out_buf, out_len, key_s, 1)
    return bytearray(cffienv.FFI.buffer(out_buf, n))

def encrypt_aes_128_ecb(in_buf, key):
    cffienv = OpenSSLCFFI()
    in_len = len(in_buf)
    out_len = in_len + 128
    out_buf = cffienv.FFI.new("unsigned char[]", out_len)
    in_buf_s = str(in_buf)
    key_s = str(key)
    n = cffienv.C.encrypt_aes_128_ecb(in_buf_s, in_len, out_buf, out_len, key_s, 1)
    return bytearray(cffienv.FFI.buffer(out_buf, n))

def encrypt_aes_128_cbc(in_buf_intact, key, iv=None):
    # we handle only bytearrays!
    key_len = 16
    in_buf = bytearray(in_buf_intact)
    pkcs7_pad(in_buf, key_len)
    cffienv = OpenSSLCFFI()
    key_s = str(key)
    nv = iv or bytearray(key_len)
    in_len = len(in_buf)
    out_buf = cffienv.FFI.new("unsigned char[]", key_len)
    ret_buf = bytearray()
    for idx in xrange(0, in_len, key_len):
        blk = fixed_xor(nv, in_buf[idx : idx + key_len])
        n = cffienv.C.encrypt_aes_128_ecb(str(blk), key_len, out_buf, key_len, key_s, 0)
        nv = bytearray(cffienv.FFI.buffer(out_buf, n))
        ret_buf = ret_buf + nv
    return ret_buf

def decrypt_aes_128_cbc(in_buf, key, iv=None, unpad=True):
    key_len = 16
    cffienv = OpenSSLCFFI()
    key_s = str(key)
    nv = iv or bytearray(key_len)
    out_buf = cffienv.FFI.new("unsigned char[]", key_len)
    ret_buf = bytearray()
    for idx in xrange(0, len(in_buf), key_len):
        n = cffienv.C.decrypt_aes_128_ecb(str(in_buf[idx : idx + key_len]), key_len, out_buf, key_len, key_s, 0)
        plain_blk = fixed_xor(nv, bytearray(cffienv.FFI.buffer(out_buf, n)))
        nv = in_buf[idx : idx + key_len]
        ret_buf = ret_buf + plain_blk
    if unpad:
        pkcs7_unpad(ret_buf, key_len)
    return ret_buf

def key_stream_aes_128_ctr(key, nonce, block_count):
    counter = nonce + bytearray(struct.pack('<Q', block_count))
    ks = encrypt_aes_128_ecb(counter, key)
    return ks

def decrypt_aes_128_ctr(in_buf, key, nonce=None):
    # fixed format:
    # 64 bit unsigned little endian nonce
    # 64 bit little endian block count (byte count / 16)
    if nonce is None:
        nonce = bytearray(8)
    n_block = (len(in_buf) + KEY_LEN - 1) / KEY_LEN
    plain = bytearray()
    for x in range(n_block):
        ks = key_stream_aes_128_ctr(key, nonce, x)
        start = x * KEY_LEN
        end = min((x + 1) * KEY_LEN, len(in_buf))
        plain += fixed_xor(in_buf[start:end], ks)
    return plain
