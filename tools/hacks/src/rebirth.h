#ifndef __REBIRTH_TYPES_H__
#define __REBIRTH_TYPES_H__

#include "types.h"

#define STACK_ALIGN() { vu128 pad __attribute__((aligned(16))); asm("":"=r"(pad):); }

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

#endif /* __REBIRTH_TYPES_H__ */