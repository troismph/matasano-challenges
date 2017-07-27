#include "stdafx.h"
#include "rc4.h"

RC4KeyStream::RC4KeyStream(unsigned char key[], int length)
{
	for (int k = 0; k<256; k++)
	{
		s[k] = k;
	}

	j = 0;

	for (i = 0; i<256; i++)
	{
		j = (j + s[i] + key[i % length]) % 256;
		swap(i, j);
	}

	i = j = 0;
}

void RC4KeyStream::swap(int a, int b)
{
	unsigned char temp = s[i];
	s[i] = s[j];
	s[j] = temp;
}

unsigned char RC4KeyStream::getbyte(void)
{
	i = (i + 1) % 256;
	j = (j + s[i]) % 256;
	swap(i, j);
	int index = (s[i] + s[j]) % 256;
	return s[index];
}
