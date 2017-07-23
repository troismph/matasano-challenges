#pragma once
#include <inttypes.h>


void uint32_to_chars(uint32_t i, unsigned char buf[4]);

uint32_t chars_to_uint32(unsigned char buf[4]);

void chars_to_hex(unsigned char* buf_in, uint32_t s_in, char* buf_out, uint32_t s_out);

template<typename T>
void set_bit(T& x, uint32_t pos, uint32_t val) {
	if (val == 1) {
		x = x | (1 << pos);
	}
	else {
		x = x & (~(1 << pos));
	}
};

uint32_t get_bit(uint32_t x, uint32_t pos);

#define H_A 0
#define H_B 1
#define H_C 2
#define H_D 3

// name: must be H_A, H_B, H_C, or H_D
// pos: bit position starting from 1
uint32_t getter(uint32_t name, uint32_t seq, uint32_t pos, uint32_t* t);

uint32_t getter(uint32_t v, uint32_t pos);

// pos: bit position starting from 1
void setter(uint32_t& x, uint32_t pos, uint32_t val);

uint32_t rrot(uint32_t x, uint32_t n);

//uint32_t rev_phy0(uint32_t h[4], uint32_t r, uint32_t y);
#define rev_phy0(h, r, y) (rrot(y, r) - h[0] - F(h[1], h[2], h[3]))

//uint32_t rev_phy1(uint32_t h[4], uint32_t r, uint32_t y);
#define rev_phy1(h, r, y) (rrot(y, r) - h[0] - G(h[1], h[2], h[3]) - 0x5a827999)

//uint32_t rev_phy2(uint32_t h[4], uint32_t r, uint32_t y);
#define rev_phy2(h, r, y) (rrot(y, r) - h[0] - H(h[1], h[2], h[3]) - 0x6ed9eba1)

//uint32_t rev_phy(uint32_t s, uint32_t h[4], uint32_t r, uint32_t y);

void get_companion(unsigned char msg[64], unsigned char companion[64]);
