from rsa_g4z3 import rsa_sign, rsa_validate, rsa_gen_key
from converts import sha256, big_int_to_bin_str, bin_str_to_big_int
import sys


def forge_sig(msg):
    # ensure that n be multiple of 3
    n_try = 10
    found = False
    for i in range(n_try):
        print "Forging, round {n}".format(n=i)
        tuner = "" if i == 0 else chr(ord('a') + i)
        msg_tune = msg + tuner
        digest = sha256(msg_tune)
        asn = big_int_to_bin_str(len(digest), 4)
        d_str = '\x00' + asn + digest  # 34B part D
        d = bin_str_to_big_int(d_str)
        n = (1 << 296) - d
        if n % 3 == 0:
            found = True
            break
    if not found:
        return None
    root = (1 << 1019) - (n * (1 << 34) / 3)
    root_str = big_int_to_bin_str(root)
    return msg_tune, '\x00' * (384 - len(root_str)) + root_str


def crack():
    msg = "I'm a nasty message."
    print "Message:{m}".format(m=msg)
    print "Generating 3072-bit rsa key pair...",
    sys.stdout.flush()
    pk, sk = rsa_gen_key(len=3072, e=3)
    print "OK"
    msg_tune, sig = forge_sig(msg)
    print "Forged message:{m}\nForged signature:{f}".format(m=msg_tune, f=sig.encode('hex'))
    assert sig is not None, "Failed to forge signature"
    assert rsa_validate(msg_tune, sig, pk, True), "Forgery invalidated"
    print "Pass"
