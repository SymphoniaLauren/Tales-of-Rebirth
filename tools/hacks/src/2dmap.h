#ifndef __2DMAP_H__
#define __2DMAP_H__

#include "types.h"
#include "rebirth.h"

typedef struct unk_btl_sub1 {
    u8 unk0[0x49];
    u8 unk49[4];
    u8 unk4D;
    u8 unk4E;
    u8 unk4F;
    u8 unk50;
    u8 unk51;
    u8 unk52;
    u8 unk53;
    u8 unk54;
    u8 unk55;
    u8 unk56;
    u8 unk57;
    u8 unk58;
    u8 unk59;
    s8 unk5A;
    u8 unk5B;
    u8 unk5C;
    u8 unk5D;
} unk_btl_sub1;

typedef struct unk_btl_sub2 {
    s16 unk0;
    s16 unk2;
    s16 unk4;
} unk_btl_sub2;

typedef struct unk_btl_sub0 {
    u8 unk0[0x2e4];
    u32 unk2E4;
    u8 unk2E8[0x320 - 0x2E8];
    unk_btl_sub2 unk320[1];
    u8 unk326[0x340 - 0x326];
    unk_btl_sub1* unk340;
    u8 unk344[0x419 - 0x344];
    u8 unk419;
} unk_btl_sub0;

// typedef struct unk_struct_0 {
//     u8 color_rgba[0x14];
// } unk_struct_0;

typedef struct _btl_struct {
    u8 unk0[0x8120];
    u32 unk8120;
    u8 unk8124[0xb388 - 0x8124];
    s8 unkB388;
    unk_btl_sub0* unkB38C;
    u8 unkC5CF[0xc5cf - 0xB390];
    fontenv_struct fontenv_0;
} btl_struct;

typedef struct _spoint {
    u16 x;
    u16 y;
} spoint;


#endif /* __2DMAP_H__ */