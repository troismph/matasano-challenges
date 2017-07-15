#include "md4_g4z3.h"
#include <assert.h>
#include <stdio.h>


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


