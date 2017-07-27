// rc4test.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <iomanip>
#include "rc4.h"

void try_run() {
	char* keys[3] = {
		"keykeykeykey",
		"qpwiotrqegfqerf",
		"23453tvgrg45tgwefv"
	};
	char* plains[3] = {
		"hahahaha",
		"lorem ipsum shall do!",
		"a quick brown fox jumps over a lazy dog"
	};
	for (uint32_t i = 0; i < 3; i++) {
		std::cout << "key=" << keys[i] << std::endl << "plain=" << plains[i] << std::endl;
		RC4KeyStream keystream((unsigned char*)keys[i], strlen(keys[i]));
		uint32_t l;
		l = strlen(plains[i]);
		uint32_t j = 0;
		unsigned char buf;
		std::cout << "cipher=";
		for (j = 0; j < l; j++) {
			unsigned char key_byte = keystream.getbyte();
			unsigned char plain_byte = plains[i][j];
			buf = plain_byte ^ key_byte;
			std::cout << std::setfill('0') << std::setw(2) << std::hex << (uint32_t)buf;
		}
		std::cout << std::endl;
	}
}

void parseargs(int argc, char ** argv, std::string & key, std::string & file, bool & hex)
{
	bool readkey = false;
	bool readfile = false;
	bool toomanyargs = false;

	for (int i = 1; i<argc; i++)
	{
		std::string arg = argv[i];
		if (arg == "-h")
		{
			hex = true;
		}
		else if (arg == "-t") {
			try_run();
			exit(0);
		}
		else if (!readkey)
		{
			key = arg;
			readkey = true;
		}
		else if (!readfile)
		{
			file = arg;
			readfile = true;
		}
		else
		{
			toomanyargs = true;
		}
	}

	if (toomanyargs || !readfile || !readkey)
	{
		std::cout << "Usage is: " << argv[0] << " [-h] key file" << std::endl;
		exit(EXIT_FAILURE);
	}

	return;
}

void gethexdigit(char in, unsigned char & out)
{
	if (in >= '0' && in <= '9')
	{
		out += in - '0';
	}
	else if (in >= 'a' && in <= 'f')
	{
		out += in - 'a' + 10;
	}
	else
	{
		std::cout << "Hex key contains letter outside range 0-9 or a-z: " << in << std::endl;
		exit(EXIT_FAILURE);
	}
}



int gethexkey(unsigned char data[], std::string key)
{
	if (key.length() % 2) //key must be of even length if it's hex
	{
		std::cout << "Hex key must have an even number of characters" << std::endl;
		exit(EXIT_FAILURE);
	}

	if (key.length() > 512)
	{
		std::cout << "Hex key cannot be longer than 512 characters long" << std::endl;
		exit(EXIT_FAILURE);
	}

	unsigned char byte;
	size_t i;

	for (i = 0; i < key.length(); i++)
	{
		gethexdigit(key[i], byte);
		byte <<= 4;
		i++;
		gethexdigit(key[i], byte);
		data[(i - 1) / 2] = byte;
	}
	return i / 2;
}

int gettextkey(unsigned char data[], std::string key)
{
	if (key.length() > 256)
	{
		std::cout << "ASCII key must be 256 characters or less" << std::endl;
		exit(EXIT_FAILURE);
	}

	size_t i;

	for (i = 0; i<key.length(); i++)
	{
		data[i] = key[i];
	}

	return i;
}

/*
void chars_to_hex(unsigned char* buf_in, uint32_t s_in, char* buf_out, uint32_t s_out) {
	stringstream ss;
	for (uint32_t i = 0; i < s_in; i++) {
		ss << std::setfill('0') << std::setw(2) << std::hex << (uint32_t)buf_in[i];
	}
	ss.str().copy(buf_out, s_out, 0);
}
*/

int main(int argc, char **argv)
{
	std::string key, file;
	bool hex = false;
	parseargs(argc, argv, key, file, hex);

	int len = 0;
	unsigned char keydata[256];

	if (hex)
		len = gethexkey(keydata, key);
	else
		len = gettextkey(keydata, key);

	RC4KeyStream bytestream(keydata, len);

	std::fstream infile;
	infile.open(file.c_str(), std::ios::in | std::ios::binary);
	if (!infile.is_open())
	{
		std::cout << file.c_str() << " does not exist" << std::endl;
		exit(EXIT_FAILURE);
	}

	if (file.find(".rc4", file.length() - 4) != std::string::npos) //ie, if file ends with ".rc4"
	{
		file.erase(file.length() - 4);
	}
	else
	{
		file.append(".rc4");
	}

	std::fstream outfile;
	outfile.open(file.c_str(), std::ios::in);
	if (outfile.is_open()) //file we are going to write to exists!
	{
		std::cout << file.c_str() << " already exists, aborting to preserve it" << std::endl;
		exit(EXIT_FAILURE);
	}

	outfile.close();
	outfile.open(file.c_str(), std::ios::out | std::ios::binary);
	if (outfile.is_open()) //Test if we were able to open the file for writing
	{
		char inbyte;
		char outbyte;
		unsigned char streambyte;

		infile.get(inbyte);

		while (!infile.eof())
		{
			streambyte = bytestream.getbyte();
			outbyte = inbyte ^ streambyte;
			outfile.put(outbyte);
			infile.get(inbyte);
		}
	}
	else
	{
		std::cout << "Could not open " << file.c_str() << " for writing\n" << std::endl;
		exit(EXIT_FAILURE);
	}

	outfile.close();
	infile.close();

	std::cout << "Encryption finished, output to " << file.c_str() << std::endl;

	return 0;
}