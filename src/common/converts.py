#!/usr/bin/python

def unhex(s):
    def unhex_byte(ss):
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
        chips = [s[x - 2 if x - 2 > 0 else None : x] \
                 for x in range(len(ss), 0, -2)]
        for chip in reversed(chips):
            v = unhex_byte(chip)
            yield v

    r = bytearray(unhex_bytes_it(s))
    return r

def b64encode(s):
    # s must be a bytearray
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

    npad = (3 - len(s) % 3) % 3
    s = s + bytearray([0 for x in range(npad)])

    sout = ''
    for i in range(0, len(s), 3):
        sout = sout + alphabet[(s[i] & 0xfc) >> 2]
        sout = sout + alphabet[((s[i] & 0x03) << 4) + (s[i + 1] >> 4)]
        c = ((s[i + 1] & 0x0f) << 2) + ((s[i + 2] & 0xc0) >> 6)
        d = s[i + 2] & 0x3f
        if i + 3 == len(s):
            if npad == 2:
                c = c if c else -1
                d = d if d else -1
            elif npad == 1:
                d = d if d else -1
        sout = sout + alphabet[c] + alphabet[d]
    return sout

def fixed_xor(buffer_a, buffer_b):
    assert(len(buffer_a) == len(buffer_b))
    buffer_c = bytearray(len(buffer_a))
    for i in range(len(buffer_a)):
        buffer_c[i] = buffer_a[i] ^ buffer_b[i]
    return buffer_c

def xor_cipher(plain, key):
    assert(len(key) == 1)
    return bytearray(map(lambda x: x ^ key[0], plain))
