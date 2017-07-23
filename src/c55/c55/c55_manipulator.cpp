#include "stdafx.h"
#include "c55_manipulator.h"
#include "c55_helpers.h"
#include <string.h>


void cs_0(uint32_t& v, uint32_t* t) {
	setter(v, 7, getter(H_B, 0, 7, t));
}

void cs_1(uint32_t& v, uint32_t* t) {
	setter(v, 7, 0);
	setter(v, 8, getter(H_A, 1, 8, t));
	setter(v, 11, getter(H_A, 1, 11, t));
}

void cs_2(uint32_t& v, uint32_t* t) {
	setter(v, 7, 1);
	setter(v, 8, 1);
	setter(v, 11, 0);
	setter(v, 26, getter(H_D, 1, 26, t));
}

void cs_3(uint32_t& v, uint32_t* t) {
	setter(v, 7, 1);
	setter(v, 8, 0);
	setter(v, 11, 0);
	setter(v, 26, 0);
}

void cs_4(uint32_t& v, uint32_t* t) {
	setter(v, 8, 1);
	setter(v, 11, 1);
	setter(v, 26, 0);
	setter(v, 14, getter(H_B, 1, 14, t));
}

void cs_5(uint32_t& v, uint32_t* t) {
	setter(v, 14, 0);
	setter(v, 19, getter(H_A, 2, 19, t));
	setter(v, 20, getter(H_A, 2, 20, t));
	setter(v, 21, getter(H_A, 2, 21, t));
	setter(v, 22, getter(H_A, 2, 22, t));
	setter(v, 26, 1);
}

void cs_6(uint32_t& v, uint32_t* t) {
	setter(v, 13, getter(H_D, 2, 13, t));
	setter(v, 14, 0);
	setter(v, 15, getter(H_D, 2, 15, t));
	setter(v, 19, 0);
	setter(v, 20, 0);
	setter(v, 21, 1);
	setter(v, 22, 0);
}

void cs_7(uint32_t& v, uint32_t* t) {
	setter(v, 13, 1);
	setter(v, 14, 1);
	setter(v, 15, 0);
	setter(v, 17, getter(H_C, 2, 17, t));
	setter(v, 19, 0);
	setter(v, 20, 0);
	setter(v, 21, 0);
	setter(v, 22, 0);
}

void cs_8(uint32_t& v, uint32_t* t) {
	setter(v, 13, 1);
	setter(v, 14, 1);
	setter(v, 15, 1);
	setter(v, 17, 0);
	setter(v, 19, 0);
	setter(v, 20, 0);
	setter(v, 21, 0);
	setter(v, 22, 1);
	setter(v, 23, getter(H_B, 2, 23, t));
	setter(v, 26, getter(H_B, 2, 26, t));
}

void cs_9(uint32_t& v, uint32_t* t) {
	setter(v, 13, 1);
	setter(v, 14, 1);
	setter(v, 15, 1);
	setter(v, 17, 0);
	setter(v, 20, 0);
	setter(v, 21, 1);
	setter(v, 22, 1);
	setter(v, 23, 0);
	setter(v, 26, 1);
	setter(v, 30, getter(H_A, 3, 30, t));
}

void cs_10(uint32_t& v, uint32_t* t) {
	setter(v, 17, 1);
	setter(v, 20, 0);
	setter(v, 21, 0);
	setter(v, 22, 0);
	setter(v, 23, 0);
	setter(v, 26, 0);
	setter(v, 30, 1);
	setter(v, 32, getter(H_D, 3, 32, t));
}

void cs_11(uint32_t& v, uint32_t* t) {
	setter(v, 20, 0);
	setter(v, 21, 1);
	setter(v, 22, 1);
	setter(v, 23, getter(H_C, 3, 23, t));
	setter(v, 26, 1);
	setter(v, 30, 0);
	setter(v, 32, 0);
}

void cs_12(uint32_t& v, uint32_t* t) {
	setter(v, 23, 0);
	setter(v, 26, 0);
	setter(v, 27, getter(H_B, 3, 27, t));
	setter(v, 29, getter(H_B, 3, 29, t));
	setter(v, 30, 1);
	setter(v, 32, 0);
}

void cs_13(uint32_t& v, uint32_t* t) {
	setter(v, 23, 0);
	setter(v, 26, 0);
	setter(v, 27, 1);
	setter(v, 29, 1);
	setter(v, 30, 0);
	setter(v, 32, 1);
}

void cs_14(uint32_t& v, uint32_t* t) {
	setter(v, 19, getter(H_D, 4, 19, t));
	setter(v, 23, 1);
	setter(v, 26, 1);
	setter(v, 27, 0);
	setter(v, 29, 0);
	setter(v, 30, 0);
}

void cs_15(uint32_t& v, uint32_t* t) {
	setter(v, 19, 0);
	setter(v, 26, 1);
	setter(v, 27, 1);
	setter(v, 29, 1);
	setter(v, 30, 0);
}

void cs_16(uint32_t& v, uint32_t* t) {
	setter(v, 19, getter(H_C, 4, 19, t));
	setter(v, 26, 1);
	setter(v, 27, 0);
	setter(v, 29, 1);
	setter(v, 32, 1);
}

void cs_17(uint32_t& v, uint32_t* t) {
	setter(v, 19, getter(H_A, 5, 19, t));
	setter(v, 26, getter(H_B, 4, 26, t));
	setter(v, 27, getter(H_B, 4, 27, t));
	setter(v, 29, getter(H_B, 4, 29, t));
	setter(v, 32, getter(H_B, 4, 32, t));
}

void cs_18(uint32_t& v, uint32_t* t) {
	setter(v, 26, getter(H_D, 5, 26, t));
	setter(v, 27, getter(H_D, 5, 27, t));
	setter(v, 29, getter(H_D, 5, 29, t));
	setter(v, 30, getter(H_D, 5, 30, t));
	setter(v, 32, getter(H_D, 5, 32, t));
}

void cs_19(uint32_t& v, uint32_t* t) {
	setter(v, 29, getter(H_C, 5, 29, t));
	setter(v, 30, 1);
	setter(v, 32, 0);
}

void cs_20(uint32_t& v, uint32_t* t) {
	setter(v, 29, 1);
	setter(v, 32, 1);
}

void cs_21(uint32_t& v, uint32_t* t) {
	setter(v, 29, getter(H_B, 5, 29, t));
}

void cs_22(uint32_t& v, uint32_t* t) {
	setter(v, 29, getter(H_D, 6, 29, t));
	setter(v, 30, 1 - getter(H_D, 6, 30, t));
	setter(v, 32, 1 - getter(H_D, 6, 32, t));
}

void cs_35(uint32_t& v, uint32_t* t) {
	setter(v, 32, 1);
}

void cs_36(uint32_t& v, uint32_t* t) {
	setter(v, 32, 1);
}

void(*cs_funcs[37])(uint32_t& v, uint32_t* t) = {
	cs_0,
	cs_1,
	cs_2,
	cs_3,
	cs_4,
	cs_5,
	cs_6,
	cs_7,
	cs_8,
	cs_9,
	cs_10,
	cs_11,
	cs_12,
	cs_13,
	cs_14,
	cs_15,
	cs_16,
	cs_17,
	cs_18,
	cs_19,
	cs_20,
	cs_21,
	cs_22,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL,
	cs_35,
	cs_36
};

/**	Correct hash states according to Table 6 of Wang05
*/
uint32_t correct_state(uint32_t s, uint32_t v, uint32_t* t) {
	uint32_t tmp = v;
	cs_funcs[s](tmp, t);
	return tmp;
}

Manipulator::Manipulator()
{
}

void Manipulator::reset(uint32_t m[16], uint32_t* t)
{
	_m = m;
	_trace = t;
	_step = 0;
}

uint32_t Manipulator::go(uint32_t r, uint32_t word_idx, uint32_t h_next, uint32_t h_rot[4], uint32_t lrot_offset)
{
	if ((_step > 22 && _step < 35) || _step > 36) {
		return h_next;
	}
	uint32_t h_c = h_next;
	cs_funcs[_step](h_c, _trace);
	int32_t m_c;
	uint32_t rev_idx = (_step % 48) / 16;
	switch (rev_idx) {
	case 0:
		m_c = rev_phy0(h_rot, lrot_offset, h_c);
		break;
	case 1:
		m_c = rev_phy1(h_rot, lrot_offset, h_c);
		break;
	case 2:
		m_c = rev_phy2(h_rot, lrot_offset, h_c);
		break;
	}
	//uint32_t m_c = rev_phy(_step, h_rot, lrot_offset, h_c);
	_m[word_idx] = m_c;
	_step++;
	return h_c;
}
