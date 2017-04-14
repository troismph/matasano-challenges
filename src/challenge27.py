from converts import encrypt_aes_128_cbc, decrypt_aes_128_cbc, fixed_xor, pkcs7_pad
from os import urandom


KEY_LEN = 16
KEY = bytearray(urandom(KEY_LEN))


def encrypter(plain):
    """
    A Key = IV encrypter
    :param plain: plain text
    :type plain: bytearray
    :param key: key, also IV
    :type key: bytearray
    :return: cipher
    :rtype: bytearray
    """
    return encrypt_aes_128_cbc(plain, KEY, KEY)


def decrypter(cipher):
    plain = decrypt_aes_128_cbc(cipher, KEY, KEY, unpad=False)
    for x in plain:
        if x > 127:
            return False, plain
    return True, None


def cracker():
    plain = bytearray("P" * (KEY_LEN * 3))
    cipher = encrypter(plain)
    c0 = cipher[0:KEY_LEN]
    cipher_attack = c0 + bytearray([0] * KEY_LEN) + c0 + plain[3*KEY_LEN:4*KEY_LEN]
    ret, plain_victim = decrypter(cipher_attack)
    if ret:
        print "Failed"
        return
    iv = fixed_xor(plain_victim[0:KEY_LEN], plain_victim[2*KEY_LEN:3*KEY_LEN])
    if iv == KEY:
        print "Pass"
    else:
        print "Failed, incorrect IV"
        print KEY
        print iv


cracker()
