#pragma once
#include "Sub_Types.h"
#include "Util.h"

const int Battle_Table_Count = 1;

const Voice_Line mao_line1 = {
    1,
    0,
    0,
    160,
    "\x05\x05\x00\x00\x00\x0b\x02\x00\x00\x00\x05\x07\x00\x00\x00: Tch! I let my guard down."
};
const Voice_Line mao_line2 = {
    1,
    0,
    166,
    0xFFFF,
    "\x05\x05\x00\x00\x00\x0b\x02\x00\x00\x00\x05\x07\x00\x00\x00: We can't have that!"
};
static const Voice_Line* mao_lines1[] = { &mao_line1, &mao_line2 };
const Battle_Subs_Table battle_subs_tables[1] = {
    {
        0x0B00001C,
        2,
        mao_lines1
    }
};