from challenge21 import MT19937
from converts import xor_cipher


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
    rng = MT19937(998765)
    rounds = 1000
    min_len = 7
    max_len = 1024
    failed = False
    for x in range(rounds):
        l = (rng.get_next() % max_len) + min_len
        seed = rng.get_next() % 0xFFFF
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
