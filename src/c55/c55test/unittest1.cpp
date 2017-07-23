#include "stdafx.h"
#include "CppUnitTest.h"
#include "c55_helpers.h"
#include "c55_collision_finder.h"
#include "md4_g4z3.h"
#include <random>
#include <time.h>


using namespace std;
using namespace Microsoft::VisualStudio::CppUnitTestFramework;

namespace c55test
{		
	TEST_CLASS(UnitTest1)
	{
	public:
		
		TEST_METHOD(TestBitOps)
		{
			uint32_t x = 0b101010101110;
			Assert::AreEqual((uint32_t)0, get_bit(x, 0));
			Assert::AreEqual((uint32_t)1, get_bit(x, 1));
			Assert::AreEqual((uint32_t)0, get_bit(x, 4));
			Assert::AreEqual((uint32_t)1, get_bit(x, 5));
			Assert::AreEqual((uint32_t)0, get_bit(x, 25));
			uint32_t y = x;
			set_bit(y, 0, 1);
			Assert::AreEqual((uint32_t)0b101010101111, y);
			y = x;
			set_bit(y, 1, 1);
			Assert::AreEqual((uint32_t)0b101010101110, y);
			y = x;
			set_bit(y, 2, 0);
			set_bit(y, 9, 0);
			Assert::AreEqual((uint32_t)0b100010101010, y);
		}

		TEST_METHOD(TestWrappers)
		{
			uint32_t t[12] = { 0b10101010, 0b01010101, 0b00001111, 0b11110000,
				0b11100011, 0b00011100, 0b00110011, 0b11001100,
				0b11100001, 0b10000010, 0b00111101, 0b11011000 };
			Assert::AreEqual((uint32_t)0, getter(H_A, 0, 1, t));
			Assert::AreEqual((uint32_t)1, getter(H_A, 0, 4, t));
			Assert::AreEqual((uint32_t)0, getter(H_C, 0, 5, t));
			Assert::AreEqual((uint32_t)1, getter(H_A, 1, 6, t));
			Assert::AreEqual((uint32_t)0, getter(H_D, 1, 7, t));
			Assert::AreEqual((uint32_t)1, getter(H_B, 2, 8, t));
		}

		TEST_METHOD(TestRevPhy)
		{
			mt19937 rg;
			rg.seed((uint32_t)time(NULL));
			for (uint32_t i = 0; i < 1000; i++)
			{
				uint32_t h[4];
				for (uint32_t j = 0; j < 4; j++)
					h[j] = rg();
				uint32_t m = rg();
				uint32_t s = rg() % 32;
				uint32_t h_next = phy0(h, m, s);
				uint32_t m_ = rev_phy0(h, s, h_next);
				Assert::AreEqual(m, m_);
				h_next = phy1(h, m, s);
				m_ = rev_phy1(h, s, h_next);
				Assert::AreEqual(m, m_);
				h_next = phy2(h, m, s);
				m_ = rev_phy2(h, s, h_next);
				Assert::AreEqual(m, m_);
			}
		}

		TEST_METHOD(Playground)
		{
			uint64_t m = ((uint64_t)1) << 32;
			uint32_t x = 999;
			Assert::AreEqual((uint64_t)999, x % m);
			Assert::AreEqual((uint32_t)999, (uint32_t)(x % m));
			int32_t y = -10;
			uint32_t uy = (uint32_t)y;
			uint32_t sy = UINT32_MAX - 9;
			Assert::AreEqual(uy, sy);
			uint32_t my = y % m;
			Assert::AreEqual(my, uy);
		}

		void get_companion_word(uint32_t msg[16], uint32_t out[16])
		{
			memcpy(out, msg, 64);
			set_bit(out[1], 31, 1);
			set_bit(out[2], 31, 1);
			set_bit(out[2], 28, 0);
			set_bit(out[12], 16, 0);
		}
		
		TEST_METHOD(TestCompanion)
		{
			mt19937 rg;
			rg.seed((uint32_t)time(NULL));
			for (uint32_t i = 0; i < 1000; i++)
			{
				uint32_t msg_words[16];
				uint32_t out_words[16];
				unsigned char out_words_bytes[64];
				unsigned char msg_bytes[64];
				unsigned char out_bytes[64];
				for (uint32_t j = 0; j < 16; j++)
				{
					msg_words[j] = rg();
					uint32_to_chars(msg_words[j], msg_bytes + 4 * j);
				}
				get_companion_word(msg_words, out_words);
				for (uint32_t j = 0; j < 16; j++)
					uint32_to_chars(out_words[j], out_words_bytes + j * 4);
				get_companion(msg_bytes, out_bytes);
				Assert::AreEqual(0, memcmp(out_words_bytes, out_bytes, 64));
			}
		}
	};
}