from converts import decrypt_aes_128_ecb, b64decode, encrypt_aes_128_ctr, key_stream_aes_128_ctr, fixed_xor
from os import urandom


KEY_LEN = 16
KEY = bytearray(urandom(16))
NONCE = bytearray(urandom(8))


def prep_cipher():
    with open('25.txt') as f:
        ecb_cipher = b64decode(f.read().replace('\n', ''))
    plain = decrypt_aes_128_ecb(ecb_cipher, bytearray("YELLOW SUBMARINE"))
    cipher = encrypt_aes_128_ctr(plain, KEY, NONCE)
    return cipher, plain


def target(cipher, offset, new_text):
    """
    To make it simpler, offset on blocks instead of bytes.
    New text must also be a whole block-long.
    :param cipher: original cipher
    :type cipher: bytearray
    :param offset: offset in block number
    :type offset: int
    :param new_text: block of plain text to be set into
    :type new_text: bytearray
    :return: the new cipher
    :rtype: bytearray
    """
    block_key = key_stream_aes_128_ctr(KEY, NONCE, offset)
    new_cipher = fixed_xor(new_text, block_key)
    start = offset * KEY_LEN
    end = min((offset + 1) * KEY_LEN, len(cipher))
    ret = bytearray(cipher)
    ret[start:end] = new_cipher
    return ret


def cracker():
    cipher, plain = prep_cipher()
    original_cipher_len = len(cipher)
    new_plain = bytearray()
    nblock = (len(cipher) + KEY_LEN - 1) / KEY_LEN
    padding = bytearray(nblock * KEY_LEN - len(cipher))
    cipher = cipher + padding
    for idx in range(0, nblock):
        cipher_sect = cipher[idx*KEY_LEN:idx*KEY_LEN+KEY_LEN]
        new_cipher = target(cipher, idx, cipher_sect)
        new_plain_sect = new_cipher[idx*KEY_LEN:idx*KEY_LEN+KEY_LEN]
        new_plain += new_plain_sect
    del new_plain[original_cipher_len:]
    print new_plain
    if new_plain == plain:
        print "Pass"
    else:
        print "Crack failed, plain text unequal"

