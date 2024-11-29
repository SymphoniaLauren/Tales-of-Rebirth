#ifndef __REBIRTH_TYPES_H__
#define __REBIRTH_TYPES_H__

#include "types.h"

#define STACK_ALIGN() { u128 pad __attribute__((aligned(16))); asm("":"=r"(pad):); }

typedef enum PACKED FILE_FLAGS {
    UNK_FLAG_0        = 0,
    IS_OVERLAY_LIKELY = (1 << 0),
    LOAD_BLOCKING     = (1 << 1),
    IS_COMPRESSED     = (1 << 2),
    UNK_FLAG_3        = (1 << 3),
    IS_IOP_MODULE     = (1 << 4),
    UNK_FLAG_10       = (1 << 10),
    UNK_FLAG_11       = (1 << 11),
    FROM_MOV_BIN      = (1 << 12),
    FROM_FLD_BIN      = (1 << 13),
    ENUM_SIZE         = 0xFFFF
} FILE_FLAGS;

typedef struct file_desc {
    void *addr;
    int file_id;
    int start_offset;
    int file_size;
    FILE_FLAGS flags;
    u8 unk12;
    u8 unk13;
} file_desc;

typedef struct fontenv_struct {
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
} fontenv_struct;

typedef struct btl_chr_struct{
    u8 unk_00[0x440];
    u32 char_id;
    u32 unk_444;
    u32 playing_voice_id;
} btl_chr_struct;

#endif /* __REBIRTH_TYPES_H__ */