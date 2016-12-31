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
