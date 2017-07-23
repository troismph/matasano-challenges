#include "stdafx.h"
#include "c55_collision_finder.h"
#include "c55_manipulator.h"
#include "c55_helpers.h"
#include "md4_sol.h"
#include <time.h>
#include <iostream>
#include <random>


using namespace std;

CollisionFinder::CollisionFinder() {
	_rand.seed((unsigned int)time(NULL));
}

void CollisionFinder::compose(unsigned char msg[64], unsigned char msg_mod[64])
{
	Manipulator manip(false);
	MD4 md4((AbstractManipulator*)&manip);
	md4.update(msg, 64);
	md4.get_m(msg_mod);
}

void CollisionFinder::get_random_msg(unsigned char buf[64])
{
	for (uint32_t i = 0; i < 64; i += 4) {
		*(uint32_t*)(buf + i) = _rand();
	}
}

void get_md4(unsigned char* msg, uint32_t s, unsigned char out[16]) {
	MD4_CTX ctx;
	MD4_Init(&ctx);
	MD4_Update(&ctx, msg, s);
	MD4_Final(out, &ctx);
}

void CollisionFinder::find_collision()
{
	unsigned char msg_buf[64];
	unsigned char mod_buf[64];
	unsigned char companion_buf[64];
	unsigned char hash0_buf[16];
	unsigned char hash1_buf[16];
	char hex0_buf[129];
	char hex1_buf[129];
	char hex2_buf[33];
	hex0_buf[128] = '\0';
	hex1_buf[128] = '\0';
	hex2_buf[32] = '\0';
	uint64_t cntr = 0;
	uint32_t wasted = 0;
	time_t start_time = time(NULL);
	while (true) {
		if ((cntr & 0xfffff) == 0xfffff) {
			time_t elapsed = time(NULL) - start_time;
			double wasted_ratio = wasted * 1.0 / cntr;
			printf("Trying %I64x, wasted %f, elapsed %lld\n", cntr, wasted_ratio, elapsed);
		}
		cntr++;
		get_random_msg(msg_buf);
		compose(msg_buf, mod_buf);
		get_companion(mod_buf, companion_buf);
		if (memcmp(mod_buf, companion_buf, 64) == 0) {
			wasted++;
			continue;
		}
		get_md4(mod_buf, 64, hash0_buf);
		get_md4(companion_buf, 64, hash1_buf);
		if (memcmp(hash0_buf, hash1_buf, 16) == 0) {
			chars_to_hex(mod_buf, 64, hex0_buf, 128);
			chars_to_hex(companion_buf, 64, hex1_buf, 128);
			chars_to_hex(hash0_buf, 16, hex2_buf, 32);
			printf("Found collision\n%s\n%s\n", hex0_buf, hex1_buf);
			printf("md4=%s\n", hex2_buf);
			break;
		}
	}
}
