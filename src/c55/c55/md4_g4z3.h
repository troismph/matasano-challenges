#pragma once
#include <stdint.h>


uint32_t F(uint32_t x, uint32_t y, uint32_t z);

uint32_t G(uint32_t x, uint32_t y, uint32_t z);

uint32_t H(uint32_t x, uint32_t y, uint32_t z);

uint32_t lrot(uint32_t x, uint32_t n);

void swap(uint32_t& a, uint32_t& b);

void rrot_list(uint32_t* x, uint32_t s, uint32_t n);

void test_rrot_list();

//uint32_t phy0(uint32_t h[], uint32_t m, uint32_t s);

#define phy0(h, m, s) (lrot(h[0] + F(h[1], h[2], h[3]) + m, s))

//uint32_t phy1(uint32_t h[], uint32_t m, uint32_t s);

#define phy1(h, m, s) (lrot(h[0] + G(h[1], h[2], h[3]) + m + 0x5a827999, s))

//uint32_t phy2(uint32_t h[], uint32_t m, uint32_t s);

#define phy2(h, m, s) (lrot(h[0] + H(h[1], h[2], h[3]) + m + 0x6ed9eba1, s))

class AbstractManipulator {

public:
	virtual void reset(uint32_t m[16], uint32_t* t) = 0;
	virtual uint32_t go(uint32_t r, uint32_t word_idx, uint32_t h_next, uint32_t h_rot[4], uint32_t lrot_offset) = 0;
};

class MD4 {

public:
	MD4(AbstractManipulator* manip=NULL);
	void update(unsigned char* m, uint32_t s);
	void digest(unsigned char d[16]);
	void get_trace(uint32_t** trace_ptr, uint32_t& s);
	void get_m(unsigned char buf[64]);

private:
	AbstractManipulator* _manip;
	uint32_t _h[4] = { 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476 };
	uint32_t _r3_idx[16] = { 0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15 };
	//uint32_t(*_phy[3])(uint32_t *h, uint32_t m, uint32_t s) = { phy0, phy1, phy2 };
	uint32_t _lrot_off[3][4] = { {3, 7, 11, 19}, {3, 5, 9, 13}, {3, 9, 11, 15} };
	unsigned char _trailing[64];
	uint32_t _trailing_len = 0;
	uint32_t _msg_len = 0;
	uint32_t _trace[256];
	uint32_t _trace_len = 0;
	uint32_t _blk_buf[16];

	uint32_t _word_idx(uint32_t r, uint32_t s);
	void _add_block(unsigned char m[64]);
};

void test_md4();
