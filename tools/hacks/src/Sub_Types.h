#pragma once

#define EXPORT extern "C"

#ifdef _MSC_VER
#define NOINLINE
#else
#define NOINLINE  __attribute__ ((noinline))
#endif

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

typedef char s8;
typedef short s16;
typedef int s32;

#define HALFWORD(x) (*(u16*)(x))
#define SIGNEDHALFWORD(x) (*(s16*)(x))
#define WORD(x) (*(u32*)(x))

#define TRUE 1
#define FALSE 0

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

struct fontenv_struct {
	u16 font_type;
	u16 unk_02;
	u16 unk_04;
	u16 unk_06;
	u32 unk_08;
	u16 x;
	u16 y;
	u16 scale_x;
	u16 scale_y;
	u16 scale_x2;
	u16 scale_y2;
	u32 unk_18;
	u32 color;
	u16 unk_20;
	u16 unk_22;
	u16 unk_24;
	u16 unk_26;
	u16 unk_28;
	u16 unk_2a;
	u16 unk_2c;
	u16 unk_2e;
	u32 unk_30;
	u32 unk_34;
	u32 unk_38;
	u32 width;
	u32 height;
	u32 unk_44;
	u32 unk_48;
	u32 unk_4c;
};

struct btl_chr_struct {
	u8 unk_00[0x440];
	u32 char_id;			// 440
	u32 unk_444;			// 444
	u32 playing_voice_id;	// 448
	u8 unk_44c[0x38];		// 44c
	u32 queued_voice_id;	// 484
};
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
	Voice_Line** Lines;
	inline bool operator ==(const u32& b)
	{
		return voice_id == b;
	}

	inline bool operator <(const u32& b)
	{
		return voice_id < b;
	}
};
struct Voice_Queue
{
	btl_chr_struct* btl_chr;
	Battle_Subs_Table* table;
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
	Voice_Line* Line;
	u32 Current_Post_Frame;
	u32 Extra_Frames;
	u32 Current_Frame;
	u32 Total_Lines;
};

struct Skit_Container
{
	char* string_1;
	char* string_2;
	int num_lines;
};