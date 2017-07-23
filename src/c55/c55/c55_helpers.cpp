#include "stdafx.h"
#include "c55_helpers.h"
#include "md4_g4z3.h"
#include <string.h>
#include <sstream>
#include <iomanip>


using namespace std;

void chars_to_hex(unsigned char* buf_in, uint32_t s_in, char* buf_out, uint32_t s_out) {
	stringstream ss;
	for (uint32_t i = 0; i < s_in; i++) {
		ss << std::setfill('0') << std::setw(2) << std::hex << (uint32_t)buf_in[i];
	}
	ss.str().copy(buf_out, s_out, 0);
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

uint32_t get_bit(uint32_t x, uint32_t pos) {
	return (x & (1 << pos)) ? 1 : 0;
}

uint32_t getter(uint32_t name, uint32_t seq, uint32_t pos, uint32_t* t) {
	uint32_t idx = 0;
	if (seq == 0)
		idx = name;
	else
		idx = seq * 4 + (4 - name) % 4;
	return get_bit(t[idx], pos - 1);
}

uint32_t getter(uint32_t v, uint32_t pos)
{
	return get_bit(v, pos - 1);
}

void setter(uint32_t & x, uint32_t pos, uint32_t val)
{
	set_bit<uint32_t>(x, pos - 1, val);
}

uint32_t rrot(uint32_t x, uint32_t n) {
	uint32_t nn = n % 32;
	return ((x >> nn) & 0xffffffff) | ((x << (32 - nn)) & 0xffffffff);
}

/*
uint32_t rev_phy0(uint32_t h[4], uint32_t r, uint32_t y) {
	uint32_t t = rrot(y, r);
	return t - h[0] - F(h[1], h[2], h[3]);
}

uint32_t rev_phy1(uint32_t h[4], uint32_t r, uint32_t y) {
	uint32_t t = rrot(y, r);
	return t - h[0] - G(h[1], h[2], h[3]) - 0x5a827999;
}

uint32_t rev_phy2(uint32_t h[4], uint32_t r, uint32_t y) {
	uint32_t t = rrot(y, r);
	return t - h[0] - H(h[1], h[2], h[3]) - 0x6ed9eba1;
}

uint32_t(*rev_phy_list[3])(uint32_t h[4], uint32_t r, uint32_t y) = {
	rev_phy0, rev_phy1, rev_phy2
};

uint32_t rev_phy(uint32_t s, uint32_t h[4], uint32_t r, uint32_t y)
{
	uint32_t idx = (s % 48) / 16;
	return rev_phy_list[idx](h, r, y);
}
*/

void get_companion(unsigned char msg[64], unsigned char companion[64]) {
	memcpy(companion, msg, 64);
	set_bit(companion[1 * 4 + 31 / 8], 7, 1);
	set_bit(companion[2 * 4 + 31 / 8], 7, 1);
	set_bit(companion[2 * 4 + 31 / 8], 4, 0);
	set_bit(companion[12 * 4 + 16 / 8], 0, 0);
}