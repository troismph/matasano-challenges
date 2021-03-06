#include <openssl/evp.h>
#include <stdio.h>

int decrypt_aes_128_ecb(unsigned char* input, unsigned int input_len,
                        unsigned char* output,  unsigned int outbuf_len,
                        unsigned char* key, int padding) {
  int outlen, finallen, ret;
  EVP_CIPHER_CTX ctx;
  EVP_CIPHER_CTX_init(&ctx);
  EVP_DecryptInit(&ctx, EVP_aes_128_ecb(), key, 0);
  if (padding == 0)
    EVP_CIPHER_CTX_set_padding(&ctx, padding);
  if (!(ret = EVP_DecryptUpdate(&ctx, output, &outlen, input, input_len))) {
    printf("DecryptUpdate Error %d\n", ret);
    return 0;
  }
  if (!(ret = EVP_DecryptFinal(&ctx, output + outlen, &finallen))) {
    printf("DecryptFinal Error %d\n", ret);
    return 0;
  }
  EVP_CIPHER_CTX_cleanup(&ctx);
  return outlen + finallen;
}

int encrypt_aes_128_ecb(unsigned char* input, unsigned int input_len,
                        unsigned char* output,  unsigned int outbuf_len,
                        unsigned char* key, int padding) {
  int outlen, finallen;
  EVP_CIPHER_CTX ctx;
  EVP_CIPHER_CTX_init(&ctx);
  EVP_EncryptInit(&ctx, EVP_aes_128_ecb(), key, 0);
  if (padding == 0)
    EVP_CIPHER_CTX_set_padding(&ctx, padding);
  if (!EVP_EncryptUpdate(&ctx, output, &outlen, input, input_len)) {
    printf("EncryptUpdate Error\n");
    return 0;
  }
  if (!EVP_EncryptFinal(&ctx, output + outlen, &finallen)) {
    printf("EncryptFinal Error\n");
    return 0;
  }
  EVP_CIPHER_CTX_cleanup(&ctx);
  return outlen + finallen;
}

