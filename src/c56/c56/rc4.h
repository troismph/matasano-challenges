#pragma once

class RC4KeyStream
{

private:
	unsigned char s[256];
	int i, j;

	void swap(int a, int b);

public:
	unsigned char getbyte(void);
	RC4KeyStream(unsigned char key[], int length);
};
