#pragma once
#include "types.h"
#include "rebirth_text.h"

#define EXPORT extern "C"

#ifdef _MSC_VER
#define NOINLINE
#else
#define NOINLINE  __attribute__ ((noinline))
#endif

#define HALFWORD(x) (*(u16*)(x))
#define SIGNEDHALFWORD(x) (*(s16*)(x))
#define WORD(x) (*(u32*)(x))

#define TRUE 1
#define FALSE 0

#define FRAME_MAX 0xFFFF
#define CAT_PAIR_TO_ID(cat, i) (((cat & 0xFF) << 0x18) | (i & 0xFFFFFF))

#define NAME(x) CYAN x WHITE

#define TYPE_NORMAL 0
#define TYPE_BOTTOM 1
#define TYPE_POST_BATTLE 2

#define QUEUE_OFF 0
#define QUEUE_QUEUED 1
#define QUEUE_PLAYING 2
#define QUEUE_PAUSE 3

#define CONTAINER_OFF 0
#define CONTAINER_ON 1
#define CONTAINER_POST 2

struct Voice_Line;
struct Voice_Table;
struct btl_chr_struct;
struct fontenv_struct;

struct Voice_Line
{
	u8 Type;
	u8 Priority;
	u16 Start_Frame;
	u16 End_Frame;
	const char String[];
};
struct Battle_Subs_Table
{
	u32 voice_id;
	int num_lines;
	const Voice_Line** Lines;
	inline bool operator ==(const u32& b) const
	{
		return voice_id == b;
	}

	inline bool operator <(const u32& b) const
	{
		return voice_id < b;
	}
};
struct Voice_Queue
{
	btl_chr_struct* btl_chr;
	const Battle_Subs_Table* table;
	u8 queue_state;
	u32 current_frame;
};

struct Text_Container
{
	u16 Container_Id;
	u16 x;
	u16 y;
	u8 container_state;
	btl_chr_struct* btl_chr;
	u32 Battle_Voice_Id;
	const Voice_Line* Line;
	u32 Current_Post_Frame;
	u32 Extra_Frames;
	u32 Current_Frame;
	u32 Total_Lines;
};

struct Skit_Container
{
	char* string;
	int num_lines;
};