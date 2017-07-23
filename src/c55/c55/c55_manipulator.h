#pragma once
#include <stdint.h>
#include <utility>
#include "md4_g4z3.h"

class Manipulator: public AbstractManipulator {

public:
	Manipulator();
	void reset(uint32_t m[16], uint32_t* t) override;
	uint32_t go(uint32_t r, uint32_t word_idx, uint32_t h_next, uint32_t h_rot[4], uint32_t lrot_offset) override;

private:
	uint32_t _step = 0;
	uint32_t* _m;
	uint32_t* _trace = NULL;
	//uint32_t(*_phy[3])(uint32_t *h, uint32_t m, uint32_t s) = { phy0, phy1, phy2 };
};
