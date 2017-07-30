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
	CipherEmitter(const unsigned char* plain, size_t plain_len) {
		assert(plain_len < 512);
		memcpy(_plain, plain, plain_len);
		_plain_len = plain_len;
		_rand.seed(999);
	}

	size_t go(unsigned char* buf, size_t buf_len) {
		unsigned char key[16];
		for (size_t i = 0; i <16; i += 4) {
			*((uint32_t*)key) = _rand();
		}
		RC4KeyStream ks(key, 16);
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

/*
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
*/

void print_stats(uint64_t stats[256]) {
	uint64_t max_idx = 0;
	uint64_t max_val = 0;
	for (uint64_t i = 0; i < 256; i++) {
		printf("[%llx, %llx], ", i, stats[i]);
		if (max_val < stats[i]) {
			max_val = stats[i];
			max_idx = i;
		}
	}
	printf("\n");
	printf("Max=[%llx, %llx]\n", max_idx, max_val);
}

void get_stats() {
	const unsigned char plain[] = "0123456789abcdefghijklmnopqrstuvwxyz";
	uint64_t stats[2][256];
	unsigned char cipher_buf[512];

	memset(stats, 0, sizeof(stats));
	CipherEmitter ce(plain, strlen((const char*)plain));
	for (size_t i = 0; i < 0xfffffff; i++) {
		ce.go(cipher_buf, 512);
		stats[0][cipher_buf[15]]++;
		stats[1][cipher_buf[31]]++;
		if ((i & 0xfffff) == 0xfffff) {
			printf("Trying %x\n", i);
		}
	}
	printf("Finished\n");
	print_stats(stats[0]);
	print_stats(stats[1]);
}


void get_key_stats(size_t target_idx, uint64_t stats[256]) {
	memset(stats, 0, 256 * 8);
	mt19937 rd;
	rd.seed(999);
	unsigned char key[16];
	uint64_t max_try = 0xfffffff;
	for (uint64_t c = 0; c < max_try; c++) {
		if ((c & 0xfffff) == 0xfffff) {
			printf("Trying %llx of %llx\n", c, max_try);
		}
		for (size_t i = 0; i < 16; i += 4) {
			*((uint32_t*)key) = rd();
		}
		unsigned char ks_byte = 0;
		RC4KeyStream ks(key, 16);
		for (size_t i = 0; i <= target_idx; i++) {
			ks_byte = ks.getbyte();
		}
		stats[ks_byte]++;
	}
}

void pad_chars(unsigned char* buf, size_t buf_len, unsigned char* s, size_t s_len, size_t leading_len) {
	assert(leading_len < 16);
	assert(buf_len >= 48);
	assert(s_len < buf_len);
	memset(buf, 0, 48);
	size_t cp_len = min(48 - leading_len, s_len);
	memcpy(buf + leading_len, s, cp_len);
}

unsigned char get_max_idx(uint64_t stats[256]) {
	size_t max_idx = 0;
	uint64_t max_val = 0;
	for (size_t i = 0; i < 256; i++) {
		if (max_val < stats[i]) {
			max_val = stats[i];
			max_idx = i;
		}
	}
	return (unsigned char)max_idx;
}

void crack_help(unsigned char* secret, size_t secret_len, unsigned char& c15, unsigned char& c31) {
	assert(secret_len >= 32);
	uint64_t stats[2][256];
	unsigned char cipher_buf[512];
	uint64_t max_try = 0xfffffff;

	memset(stats, 0, sizeof(stats));
	CipherEmitter ce(secret, 32);
	for (uint64_t i = 0; i < max_try; i++) {
		ce.go(cipher_buf, 512);
		stats[0][cipher_buf[15]]++;
		stats[1][cipher_buf[31]]++;
		if ((i & 0xfffff) == 0xfffff) {
			printf("\rTrying %llx          ", i);
		}
	}
	printf("\rFinished\n");
	c15 = get_max_idx(stats[0]) ^ 240;
	c31 = get_max_idx(stats[1]) ^ 224;
}

void crack(unsigned char* cookie, size_t cookie_len, unsigned char out_buf[32]) {
	unsigned char buf[48];
	memset(out_buf, 0, 32);
	for (size_t i = 0; i < 16; i++) {
		unsigned char c15;
		unsigned char c31;
		printf("Processing leading=%u\n", i);
		pad_chars(buf, 48, cookie, cookie_len, i);
		crack_help(buf, 48, c15, c31);
		out_buf[15 - i] = c15;
		out_buf[31 - i] = c31;
		printf("c15=%c, c31=%c\n", c15, c31);
	}
}


int main()
{
	unsigned char plain[] = "0123456789abcdefghijklmnopqrstuvwxyz";
	unsigned char out_buf[32];
	crack(plain, strlen((const char*)plain), out_buf);
    return 0;
}

