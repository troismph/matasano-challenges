#include <openssl/evp.h>
//#include "challenge7.h"

int decrypt_aes_128_ecb(unsigned char* cipher, unsigned int cipher_len,
                        unsigned char* plain,  unsigned int plain_len,
                        unsigned char* key) {
  int outlen, finallen;
  EVP_CIPHER_CTX ctx;
  EVP_CIPHER_CTX_init(&ctx);
  EVP_DecryptInit(&ctx, EVP_aes_128_ecb(), key, 0);
  EVP_CIPHER_CTX_set_padding(&ctx, 0);
  if(!EVP_DecryptUpdate(&ctx, plain, &outlen, cipher, cipher_len))
    return 0;
  if (!EVP_DecryptFinal(&ctx, plain + outlen, &finallen))
    return 0;
  EVP_CIPHER_CTX_cleanup(&ctx);
  return outlen + finallen;
}
