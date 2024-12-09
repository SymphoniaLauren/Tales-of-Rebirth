#pragma once
#include "Sub_Types.h"

extern "C"
{
	void fntenv_make_default(fontenv_struct* fntenv);
	void get_str_width(fontenv_struct* fntenv, const char str[], int width, int height);
	void draw_string(fontenv_struct* fntenv, const char str[]);
	int getBtlVoiceTimer(btl_chr_struct* btl_chr, int voice_id);
	int sprintf ( char * str, const char * format, ... );
	char* getMonsterName(int monster_id);
	char* getEncodedCharName(int cat, int id);
	int strcmp(const char* str1, const char* str2);
}
