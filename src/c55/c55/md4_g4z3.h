#pragma once
#include <stdint.h>


uint32_t F(uint32_t x, uint32_t y, uint32_t z);

uint32_t G(uint32_t x, uint32_t y, uint32_t z);

uint32_t H(uint32_t x, uint32_t y, uint32_t z);

uint32_t lrot(uint32_t x, uint32_t n);

void swap(uint32_t& a, uint32_t& b);

void rrot_list(uint32_t* x, uint32_t s, uint32_t n);

void test_rrot_list();
