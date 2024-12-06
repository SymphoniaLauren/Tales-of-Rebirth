#include "types.h"

extern u16 func_0010FC50();

DATA int is_show_debug = 0;
extern u8 map2d_linehit;
extern u16 pad_held_buttons;
extern u8 is_map2d_debug_enabled;

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
