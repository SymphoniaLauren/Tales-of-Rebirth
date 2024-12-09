#ifndef __SUBS_H__
#define __SUBS_H__

#include "types.h"

typedef struct _credit_line {
    short x;
    short y;
    u8 color;
    const char *text;
} credit_line;

typedef struct unkspad_sub
{
    s16 unk0;
    s16 unk2;
    s16 unk4;
    s16 unk6;
} unkspad_sub;

typedef struct unkspad
{
    s32 unk0;
    s32 unk4;
    s32 unk8;
    s32 unkc;
    u8 pad[0x100 - 0x10];
    s16 unk100;
    s16 unk102;
    s16 unk104;
    s16 unk106;
    unkspad_sub unk108;
    s32 unk110;
} unkspad;
typedef struct _fmv_sub
{
    int start_frame;
    const char *text;
} fmv_sub;

typedef struct _fmv_entry
{
    int sub_count;
    const fmv_sub *subs;
} fmv_entry;

#endif /* __SUBS_H__ */