# Solution for challenge 18

from converts import decrypt_aes_128_ctr, b64decode


def run():
    key = bytearray('YELLOW SUBMARINE')
    cipher = b64decode(
        'L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ=='
    )
    plain = decrypt_aes_128_ctr(cipher, key)
    print plain


run()
