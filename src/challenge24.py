from challenge21 import MT19937
from converts import xor_cipher


RNG = MT19937(879867987)


def rng_byte_stream(seed, byte_count):
    """
    Return a random bytearray with length byte_count
    :param seed: seed for random number generator
    :type seed: int
    :param byte_count: byte count
    :type byte_count: int
    :return: bytearray of random bytes
    :rtype: bytearray
    """
    ret = bytearray()
    rn_ref = []
    rng = MT19937(seed)
    byte_offset = 0
    rn = 0
    for x in range(byte_count):
        if byte_offset == 0:
            rn = rng.get_next()
            rn_ref.append(rn)
        ret.append((rn >> byte_offset) & 0xFF)
        byte_offset = (byte_offset + 8) % 32
    return ret, rn_ref


def recover_key_int(victim_slice, plain_chr):
    """
    Recover the original random number from victim slice
    :param victim_slice: 4 bytes from victim
    :type victim_slice: bytearray
    :param plain_chr: the known plain character
    :type plain_chr: str
    :return: recovered int from the random number generator
    :rtype: int
    """
    ret = 0
    plain_byte = ord(plain_chr)
    for i in range(4):
        ret_slice = victim_slice[i] ^ plain_byte
        ret = ret + (ret_slice << (i * 8))
    return ret


def test_rng_byte_stream():
    seed = 98765
    stream_len = 1024
    bs, rn = rng_byte_stream(seed, stream_len)
    rn_t = []
    for x in range(0, stream_len, 4):
        rn_t.append(recover_key_int(bs[x:x+4], '\x00'))
    if rn != rn_t:
        print "Failed"
        print rn
        print rn_t
    else:
        print "Pass"


def encrypt_rng(plain, seed):
    """
    Encrypt with RNG
    :param plain: plain text
    :type plain: bytearray
    :param seed: the key
    :type seed: int
    :return: cipher text
    :rtype: bytearray
    """
    key_stream, rn_ref = rng_byte_stream(seed, len(plain))
    cipher = xor_cipher(plain, key_stream)
    return cipher


def decrypt_rng(cipher, seed):
    return encrypt_rng(cipher, seed)


def test_rng_cipher():
    from os import urandom
    rounds = 1000
    min_len = 7
    max_len = 1024
    failed = False
    for x in range(rounds):
        l = (RNG.get_next() % max_len) + min_len
        seed = RNG.get_next() % 0xFFFF
        plain = bytearray(urandom(l))
        cipher = encrypt_rng(plain, seed)
        plain_t = decrypt_rng(cipher, seed)
        if plain != plain_t:
            failed = True
            print "Failed!"
            print plain
            print plain_t
    if not failed:
        print "Pass after {n} rounds".format(n=rounds)


def target(plain, seed):
    from os import urandom
    min_prefix_len = 7
    max_prefix_len = 30
    prefix_len = (RNG.get_next() % max_prefix_len) + min_prefix_len
    prefix = bytearray(urandom(prefix_len))
    cipher = encrypt_rng(prefix + plain, seed)
    return cipher


def cracker():
    seed = RNG.get_next() & 0xFFFF
    plain_len = 20
    plain_txt = bytearray('V') * plain_len
    cipher = target(plain_txt, seed)
    for s in range(0xFFFF):
        if s % 1000 == 0:
            print "Trying {s}".format(s=s)
        c = decrypt_rng(cipher, s)
        if c[-plain_len:] == plain_txt[-plain_len:]:
            print "Cracked, seed={s}".format(s=s)
            if s == seed:
                print "Crack pass"
                return
            else:
                print "Crack failed, should be {s}".format(s=seed)
                return
    print "No crack found"
