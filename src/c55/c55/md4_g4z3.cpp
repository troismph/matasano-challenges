#include "md4_g4z3.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <algorithm>
#include <sstream>
#include <iostream>
#include <iomanip>


using namespace std;


uint32_t F(uint32_t x, uint32_t y, uint32_t z) {
	return (x & y) | ((~x) & z);
}


uint32_t G(uint32_t x, uint32_t y, uint32_t z) {
	return (x & y) | (x & z) | (y & z);
}


uint32_t H(uint32_t x, uint32_t y, uint32_t z) {
	return x ^ y ^ z;
}


uint32_t lrot(uint32_t x, uint32_t n) {
	return (x << n) | (x >> (32 - n));
}


void swap(uint32_t& a, uint32_t& b) {
	a = a ^ b;
	b = b ^ a;
	a = a ^ b;
}


void rrot_list(uint32_t* x, uint32_t s, uint32_t n) {
	uint32_t nn = n % s;
	if (nn == 0) {
		return;
	}
	uint32_t cntr = 0;
	uint32_t thread_head = 0;
	uint32_t to = thread_head;
	while (true) {
		to = (to + nn) % s;
		if (to == thread_head && cntr < s - (thread_head + 1)) {
			thread_head++;
			to = thread_head;
			continue;
		}
		swap(x[thread_head], x[to]);
		cntr++;
		if (cntr == s - (thread_head + 1)) {
			break;
		}
	}
}


void test_rrot_list() {
	uint32_t x[] = {1, 2, 3, 4};
	rrot_list(x, 4, 1);
	for (uint32_t i = 0; i < 4; i++) {
		printf("%u,", x[i]);
	}
	printf("\n");
	assert(x[0] == 4 && x[1] == 1);
	uint32_t y[] = { 1, 2, 3, 4 };
	rrot_list(y, 4, 3);
	for (uint32_t i = 0; i < 4; i++) {
		printf("%u,", y[i]);
	}
	printf("\n");
	assert(y[0] == 2 && y[3] == 1);
	uint32_t z[] = { 1, 2, 3, 4 };
	rrot_list(z, 4, 2);
	for (uint32_t i = 0; i < 4; i++) {
		printf("%u,", z[i]);
	}
	printf("\n");
	assert(z[0] == 3 && z[1] == 4);
	printf("Test pass\n");
}


uint32_t phy0(uint32_t h[], uint32_t m, uint32_t s) {
	uint32_t t = h[0] + F(h[1], h[2], h[3]) + m;
	return lrot(t, s);
}


uint32_t phy1(uint32_t h[], uint32_t m, uint32_t s) {
	uint32_t t = h[0] + G(h[1], h[2], h[3]) + m + 0x5a827999;
	return lrot(t, s);
}


uint32_t phy2(uint32_t h[], uint32_t m, uint32_t s) {
	uint32_t t = h[0] + H(h[1], h[2], h[3]) + m + 0x6ed9eba1;
	return lrot(t, s);
}

void chars_to_hex(unsigned char* buf_in, uint32_t s_in, char* buf_out, uint32_t s_out) {
	stringstream ss;
	for (uint32_t i = 0; i < s_in; i++) {
		ss << std::setfill('0') << std::setw(2) << std::hex << (uint32_t)buf_in[i];
	}
	ss.str().copy(buf_out, s_out, 0);
}

void test_md4()
{
	char* cases[7] = {
		"",
		"a",
		"abc",
		"message digest",
		"abcdefghijklmnopqrstuvwxyz",
		"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
		"12345678901234567890123456789012345678901234567890123456789012345678901234567890"
	};
	char* md4s[7] = {
		"31d6cfe0d16ae931b73c59d7e0c089c0",
		"bde52cb31de33e46245e05fbdbd6fb24",
		"a448017aaf21d8525fc10ae87aa6729d",
		"d9130a8164549fe818874806e1c7014b",
		"d79e1c308aa5bbcdeea8ed63df412da9",
		"043f8582f241db351ce627e153e7f0e4",
		"e33b4ddc9c38f2199c3e7b164fcc0536"
	};
	char buf[32];
	for (uint32_t i = 0; i < 7; i++) {
		MD4 md4;
		md4.update((unsigned char*)cases[i], strlen(cases[i]));
		unsigned char digest[16];
		md4.digest(digest);
		chars_to_hex(digest, 16, buf, 32);
		if (memcmp(md4s[i], buf, 32) == 0) {
			printf("Pass\n");
		}
		else {
			printf("Failed %u\n", i);
			uint32_t* trace_ptr;
			uint32_t trace_size;
			md4.get_trace(&trace_ptr, trace_size);
			for (uint32_t k = 0; k < trace_size; k++) {
				printf("%u, ", trace_ptr[k]);
			}
			printf("\n");
		}
	}
}


void uint32_to_chars(uint32_t i, unsigned char buf[4]) {
	buf[0] = i & 0xff;
	buf[1] = (i >> 8) & 0xff;
	buf[2] = (i >> 16) & 0xff;
	buf[3] = (i >> 24) & 0xff;
}


uint32_t chars_to_uint32(unsigned char buf[4]) {
	return (uint32_t)buf[0] + (uint32_t)(buf[1] << 8)
		+ (uint32_t)(buf[2] << 16) + (uint32_t)(buf[3] << 24);
}


MD4::MD4()
{
}

void MD4::update(unsigned char * m, uint32_t s)
{
	unsigned char buf[64];
	_msg_len += s;

	if (_trailing_len + s < 64) {
		memcpy(_trailing + _trailing_len, m, s);
		_trailing_len += s;
	}
	else {
		memcpy(buf, _trailing, _trailing_len);

		uint32_t input_handled = 64 - _trailing_len;
		memcpy(buf + _trailing_len, m, input_handled);
		_add_block(buf);

		while (input_handled + 64 <= s) {
			memcpy(buf, m + input_handled, 64);
			_add_block(buf);
			input_handled += 64;
		}

		_trailing_len = s - input_handled;
		memcpy(_trailing, m + input_handled, _trailing_len);
	}
}

void MD4::digest(unsigned char* d)
{
	unsigned char buf[128];
	buf[0] = 0x80;
	uint32_t n_zeros = (55 - _msg_len) % 64;
	memset(buf + 1, 0, n_zeros);
	uint64_t n_bits = _msg_len << 3;
	memcpy(buf + 1 + n_zeros, &n_bits, 8);
	update(buf, 1 + n_zeros + 8);
	for (uint32_t i = 0; i < 4; i++) {
		uint32_to_chars(_h[i], d + i * 4);
	}
}

void MD4::get_trace(uint32_t ** trace_ptr, uint32_t & s)
{
	*trace_ptr = _trace;
	s = _trace_len;
}

uint32_t MD4::_word_idx(uint32_t r, uint32_t s)
{
	if (r == 0) {
		return s;
	}
	else if (r == 1) {
		return (s % 4) * 4 + (s / 4);
	}
	else {
		return _r3_idx[s];
	}
}

void MD4::_add_block(unsigned char m[64])
{
	uint32_t h[4];
	memcpy(h, _h, 16);
	uint32_t blk[16];
	for (uint32_t i = 0; i < 16; i++) {
		blk[i] = chars_to_uint32(m + i * 4);
	}
	for (uint32_t r = 0; r < 3; r++) {
		for (uint32_t s = 0; s < 16; s++) {
			uint32_t state_idx = (16 - s) % 4;
			uint32_t word_idx = _word_idx(r, s);
			uint32_t lrot_offset = _lrot_off[r][s % 4];
			//uint32_t h_rot = rrot_list(_h, 4, s % 4);
			uint32_t h_next = _phy[r](h, blk[word_idx], lrot_offset);
			h[0] = h_next;
			rrot_list(h, 4, 1);
			_trace[_trace_len] = h_next;
			_trace_len = (_trace_len + 1) % 256;
		}
	}
	for (uint32_t i = 0; i < 4; i++) {
		_h[i] = _h[i] + h[i];
	}
}


