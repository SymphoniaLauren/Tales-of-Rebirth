#include "types.h"
#include "sceio.h"

extern u16 func_0010FC50();

DATA int is_show_debug = 0;
extern u8 map2d_linehit;
extern u16 pad_held_buttons;
extern u8 is_map2d_debug_enabled;

extern u64 fontenv_tex0;
extern u64 story_tex0;
void update_tex0() {
    // The game does this nifty thing where it allocates a 64x32 texture 
    // (A "Page") for the main textures, the allocation is at the end of VRAM
    // and for some reason making the texture bigger breaks rendering, but 
    // keeping it smaller doesn't (but shuffles the palettes).
    // So we'll do a hack and shift the CBP of the relevant TEX0 registers
    // used for the text and let the rest of the game deal with the problem.
    fontenv_tex0 &= ~SCE_GS_SET_TEX0(0, 0, 0, 0, 0, 0, 0, 0x3FFF, 0, 0, 0, 0);
    story_tex0 &= ~SCE_GS_SET_TEX0(0, 0, 0, 0, 0, 0, 0, 0x3FFF, 0, 0, 0, 0);
    fontenv_tex0 |= SCE_GS_SET_TEX0(0, 0, 0, 0, 0, 0, 0, 0x3AE3, 0, 0, 0, 0);
    story_tex0 |= SCE_GS_SET_TEX0(0, 0, 0, 0, 0, 0, 0, 0x3AE3, 0, 0, 0, 0);
}

void show_debug_view() {
    u16 buttons = pad_held_buttons;

    if (!is_map2d_debug_enabled) {
        return;
    }

    if ((buttons & 0x0C) == 0x0C) {
        // if L1+R1 pressed
        is_show_debug = 1;
    } else if ((buttons & 0x03) == 0x03) {
        // if L2+R2 pressed
        is_show_debug = 0;
    }
    
    if ((buttons & 0x84) == 0x84) {
        // if L1+▢ pressed
        map2d_linehit = 0x90;
    } else if ((buttons & 0x88) == 0x88) {
        // if R1+▢ pressed
        map2d_linehit = 0x80;
    }

    if (is_show_debug) {
        map2d_DebugInit();
        map2d_DebugMessage();
    }
}
