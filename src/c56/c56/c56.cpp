// c56.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <cassert>
#include <random>
#include <algorithm>
#include "rc4.h"


using namespace std;

class CipherEmitter {
public:
	CipherEmitter(unsigned char* plain, size_t plain_len) {
		assert(plain_len < 512, "Too long plain text");
		memcpy(_plain, plain, plain_len);
		_plain_len = plain_len;
		_rand.seed(999);
	}

	size_t go(unsigned char* buf, size_t buf_len) {
		unsigned char key[64];
		for (size_t i = 0; i <64; i += 4) {
			*((uint32_t*)key) = _rand();
		}
		RC4KeyStream ks(key, 64);
		size_t ret = min(_plain_len, buf_len);
		for (size_t i = 0; i < ret; i++) {
			buf[i] = _plain[i] ^ ks.getbyte();
		}
		return ret;
	}

private:
	unsigned char _plain[512];
	size_t _plain_len;
	mt19937 _rand;
};

void print_array(uint32_t stats[2][256], size_t c, size_t l) {
	uint32_t m = 0;
	uint32_t v = 0;
	for (size_t j = 0; j < c; j++) {
		m = 0;
		v = 0;
		for (size_t i = 0; i < l; i++) {
			//printf("[%u, %u], ", i, stats[i]);
			if (m < stats[j][i]) {
				m = stats[j][i];
				v = i;
			}
		}
		printf("Max=%u, ", v);
	}
	printf("\n");
}


void get_stats() {
	size_t target_idx[2] = { 15, 31 };
	unsigned char plain[] = "0123456789012345678901234567890123456789";
	uint32_t stats[2][256];
	unsigned char cipher_buf[512];

	memset(stats, 0, 256 * 2 * 4);
	CipherEmitter ce(plain, 40);
	for (size_t i = 0; i < (1 << 30); i++) {
		ce.go(cipher_buf, 512);
		stats[0][cipher_buf[15]]++;
		stats[1][cipher_buf[31]]++;
		if ((i & 0xfffff) == 0xfffff) {
			printf("Trying %x\n", i);
			print_array(stats, 2, 256);
		}
	}
	printf("Finished\n");
	print_array(stats, 2, 256);
}



int main()
{
	get_stats();
    return 0;
}

