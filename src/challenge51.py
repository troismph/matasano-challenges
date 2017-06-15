import zlib
import os
from string import ascii_letters, digits
from converts import encrypt_aes_128_ecb, encrypt_aes_128_cbc

SID = "TmV2ZXIgcmV2ZWFsIHRoZSBXdS1UYW5nIFNlY3JldCE="
KEY = os.urandom(16)
ALPHABET = ascii_letters + digits


def enc_func(buf, key, iv=None):
    return encrypt_aes_128_cbc(buf, key, iv)


def oracle(payload, zlen=False):
    content = "POST / HTTP/1.1\n" \
              "Host: hapless.com\n" \
              "Cookie: sessionid={sid}\n" \
              "Content-Length: {len_payload}\n" \
              "{payload}".format(sid=SID, len_payload=len(payload), payload=payload)
    z_content = bytearray(zlib.compress(content, 6))
    e_z = enc_func(z_content, KEY)
    if zlen:
        return len(z_content), len(e_z)
    else:
        return len(e_z)


def edge_padding(s, amplifier):
    padding = ''
    l = oracle(s)
    for x in range(256):
        padding += chr(x)
        ll = oracle((padding + s) * amplifier)
        if ll > l:
            return padding[:-1]


def test_padding2(amplifier):
    s = 'sessionid='
    for c in SID:
        s += c
        p = edge_padding(s, 1)
        print '{s}:{p}'.format(s=s, p=p.encode('hex'))


def test_padding(s, amplifier):
    padding = ''
    z, e = oracle(s, True)
    print '{p}:{z},{e}'.format(p=padding.encode('hex'), z=z, e=e)
    for x in range(32):
        padding += chr(x)
        z_, e_ = oracle((padding + s) * amplifier, True)
        print '{p}:{z},{e}'.format(p=padding.encode('hex'), z=z_, e=e_)


def test_zlen(amplifier):
    s = '\x00\x01\x02\x03\x04sessionid='
    for c in SID:
        s += c
        z, e = oracle(s * amplifier, True)
        print '{s}:{z}, {e}'.format(s=s, z=z, e=e)


def crack_(known, target_len, amp):
    while len(known) < target_len:
        padding = edge_padding(known, amp)
        lens = [(oracle((padding + known + x) * amp), x) for x in ALPHABET]
        min_len = min(lens, key=lambda p: p[0])[0]
        cands = filter(lambda j: j[0] == min_len, lens)
        if len(cands) > 1:
            # multiple possible next byte found
            # just return, will retry with different amp
            break
        known += cands[0][1]
        print known
    return known


def crack():
    known = 'sessionid='
    # session id is a 32-byte binary, whose base64 format always terminates with =
    # so we know this base64 string has 43 alpha-numerical digits
    target_len = len(known) + 43
    amp_max = 8
    while len(known) < target_len:
        amp = 1
        while amp <= amp_max:
            print 'AMP set to {amp}'.format(amp=amp)
            prev_len = len(known)
            known = crack_(known, target_len, amp)
            post_len = len(known)
            if post_len >= target_len:
                # accomplished
                break
            if post_len > prev_len:
                # progress but not full
                # retry from amp = 1
                amp = 1
            else:
                # no progress, increase amp
                amp += 1
        if amp > amp_max:
            # failed after trying all amp
            assert False, 'Failed to find sessionid after trying max amp={amp}'.format(amp=amp_max)
    known = known + '='
    print 'Final:{k}'.format(k=known)
    assert known[10:] == SID, 'Wrong sessionid'
