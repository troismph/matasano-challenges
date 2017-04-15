from md4_bonsaiviking import MD4
import struct


def md4_pad(buf, extra_len=0):
    buf_len = len(buf) + extra_len
    return bytearray("\x80" + "\x00" * ((55 - buf_len) % 64) + struct.pack("<Q", buf_len * 8))


def test_md4_pad():
    from os import urandom
    import random
    rounds = 100
    passed = True
    for x in range(rounds):
        buf_len = random.randint(10, 2000)
        buf = urandom(buf_len)
        md4_obj = MD4()
        md4_obj.add(buf).finish()
        padded_buf = buf + md4_pad(buf)
        if padded_buf != bytearray(md4_obj.message):
            print "Failed"
            print padded_buf
            print bytearray(md4_obj.message)
            passed = False
    if passed:
        print "Pass {n} rounds".format(n=rounds)


SECRET_PREFIX = "THE POST-RAIN SUNSHINE"


def target(buf):
    md4 = MD4()
    md4.add(SECRET_PREFIX + buf)
    return md4.finish()


def crack_helper(original_msg, pay_load, oracle):
    original_hashmac = target(original_msg)
    md4_state = list(struct.unpack("<4I", original_hashmac))
    glue_padding = md4_pad(bytearray(original_msg), oracle)
    md4_obj = MD4()
    count = (oracle + len(original_msg) + len(glue_padding)) / 64
    md4_obj.set_state(md4_state, count)
    forged_hashmac = md4_obj.add(pay_load).finish()
    return original_msg + glue_padding + pay_load, forged_hashmac


def cracker():
    pay_load = ";admin=true"
    original_msg = "comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
    rounds = 100
    passed = False
    for guess_len in range(rounds):
        forged_msg, forged_hashmac = crack_helper(original_msg, pay_load, guess_len)
        verify_hashmac = target(forged_msg)
        if verify_hashmac == forged_hashmac:
            print "Pass, prefix len guess={n}".format(n=guess_len)
            print original_msg
            print forged_msg
            print forged_hashmac
            passed = True
            break
    if not passed:
        print "Fail, after {n} tries".format(n=rounds)
