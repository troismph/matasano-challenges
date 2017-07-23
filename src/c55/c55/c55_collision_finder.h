#pragma once
#include <inttypes.h>
#include <random>


class CollisionFinder {

public:
	CollisionFinder();
	void compose(unsigned char msg[64], unsigned char msg_mod[64]);
	void get_random_msg(unsigned char buf[64]);
	void find_collision();

private:
	std::mt19937 _rand;
};

