from sha1_ajalt import Sha1Hash, sha1
import struct


def sha1_pad(buf_in, extra_len=0):
    """
    SHA1 padding, buf_in left intact while padding in return value
    :param buf_in: buffer of data to be padded
    :type buf_in: bytearray
    :return: padding bytes
    :rtype: bytearray
    """
    buf_len = len(buf_in) + extra_len
    nchunk = buf_len / 64
    tail = buf_len % 64
    message = buf_in[-tail:]

    # append the bit '1' to the message
    padding = bytearray('\x80')

    # append 0 <= k < 512 bits '0', so that the resulting message length (in bytes)
    # is congruent to 56 (mod 64)
    padding += bytearray('\x00') * ((56 - (buf_len + 1) % 64) % 64)

    # append length of message (before pre-processing), in bits, as 64-bit big-endian integer
    message_bit_length = buf_len * 8
    padding += bytearray(struct.pack(b'>Q', message_bit_length))
    return padding


def test_sha1_pad():
    from os import urandom
    import random
    rounds = 100
    passed = True
    for x in range(rounds):
        buf_len = random.randint(10, 2000)
        buf = urandom(buf_len)
        sha1_obj = Sha1Hash()
        sha1_obj.update(buf).digest()
        padded_buf = buf + sha1_pad(buf)
        tail_len = len(sha1_obj.tail_chunks)
        my_tail = padded_buf[-tail_len:]
        if my_tail != bytearray(sha1.tail_chunks):
            print "Failed"
            print sha1_obj.tail_chunks
            print my_tail
            passed = False
    if passed:
        print "Pass {n} rounds".format(n=rounds)


SECRET_PREFIX = "THE POST-RAIN SUNSHINE"


def target(buf):
    return sha1(SECRET_PREFIX + buf)


def target2(buf):
    return Sha1Hash().update(SECRET_PREFIX + buf).digesttuple()


def crack_helper(original_msg, pay_load, oracle):
    original_hashmac = target(original_msg)
    sha1_state = struct.unpack(b'>IIIII', original_hashmac)
    glue_padding = sha1_pad(bytearray(original_msg), oracle)
    sha1_obj = Sha1Hash()
    sha1_obj.set_state(sha1_state, oracle + len(original_msg) + len(glue_padding))
    forged_hashmac = sha1_obj.update(pay_load).digest()
    return original_msg + glue_padding + pay_load, forged_hashmac


def cracker():
    pay_load = ";admin=true"
    original_msg = "comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon"
    forged_msg, forged_hashmac = crack_helper(original_msg, pay_load, len(SECRET_PREFIX))
    verify_hashmac = target(forged_msg)
    if verify_hashmac == forged_hashmac:
        print "Pass"
        print original_msg
        print forged_msg
        print forged_hashmac
    else:
        print "Fail"
        print verify_hashmac
        print forged_hashmac

