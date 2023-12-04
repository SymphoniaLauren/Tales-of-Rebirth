.expfunc getbyte(value, n), ((value >> (8 * (n - 1))) & 0xff)

.loadtable "./tor.tbl"

.definelabel SCOPE_LOCAL,0
.definelabel SCOPE_FILE,1
.definelabel SCOPE_ENV,2
section_7_start equ rsce_main

VEIGUE equ 0x0B, 0x01, 0x00, 0x00, 0x00
MAO    equ 0x0B, 0x02, 0x00, 0x00, 0x00
EUGENE equ 0x0B, 0x03, 0x00, 0x00, 0x00
ANNIE  equ 0x0B, 0x04, 0x00, 0x00, 0x00
TYTREE equ 0x0B, 0x05, 0x00, 0x00, 0x00
HILDA  equ 0x0B, 0x06, 0x00, 0x00, 0x00
CLAIRE equ 0x0B, 0x07, 0x00, 0x00, 0x00
AGARTE equ 0x0B, 0x08, 0x00, 0x00, 0x00
LEADER equ 0x0B, 0xFF, 0x1F, 0x00, 0x00

BLUE   equ 0x05, 0x01, 0x00, 0x00, 0x00
RED    equ 0x05, 0x02, 0x00, 0x00, 0x00
PURPLE equ 0x05, 0x03, 0x00, 0x00, 0x00
GREEN  equ 0x05, 0x04, 0x00, 0x00, 0x00
CYAN   equ 0x05, 0x05, 0x00, 0x00, 0x00
YELLOW equ 0x05, 0x06, 0x00, 0x00, 0x00
WHITE  equ 0x05, 0x07, 0x00, 0x00, 0x00
GREY   equ 0x05, 0x08, 0x00, 0x00, 0x00
BLACK  equ 0x05, 0x09, 0x00, 0x00, 0x00

.macro set_var, value
    .db 0x04
    .word value
.endmacro

.macro set_color, value
    .db 0x05
    .word value
.endmacro

.macro set_scale, value
    .db 0x06
    .word value
.endmacro

.macro set_speed, value
    .db 0x07
    .word value
.endmacro

.macro set_italic, value
    .db 0x08
    .word value
.endmacro

.macro set_number, value
    .db 0x09
    .word value
.endmacro

.macro set_text, value
    .db 0x0A
    .word value
.endmacro

.macro set_name, value
    .db 0x0B
    .word value
.endmacro

.macro set_item, value
    .db 0x0C
    .word value
.endmacro

.macro set_icon, value
    .db 0x0D
    .word value
.endmacro

.macro set_font, value
    .db 0x0E
    .word value
.endmacro

.macro set_voice, value
    .db 0x0F
    .word value
.endmacro

; push integer values into the stack
.macro push.int,value
    .if abs(value) > 0x3FFFF
        .byte 0xD8 | (value < 0 ? 0x4 : 0x0)
        .word value
    .elseif abs(value) <= 0x3FFFF && abs(value) > 0x3FF
        .byte 0xD0 | (value < 0 ? 0x4 : 0x0) | (getbyte(value, 3) & 0x3)
        .halfword value & 0xFFFF 
    .elseif abs(value) <= 0x3FF && abs(value) > 0x3
        .byte 0xC8 | (value < 0 ? 0x4 : 0x0) | (getbyte(value, 2) & 0x3)
        .byte getbyte(value, 1)
    .elseif (getbyte(abs(value), 1) & 3) <= 3
        .byte 0xC0 | (value < 0 ? 0x4 : 0x0) | (value & 0x3)
    .endif
.endmacro

.macro push.string,value 
    .byte 0xF8 | ((value & 0x30000) >> 16)
    .halfword value - text_start
.endmacro

.macro var.special
    .byte 0xFE
.endmacro

.macro var.bit,off,shift,scope
    ; bit type = 0, can only be global
    .if off <= 0x7F
        .byte (\
                /* Unused */  (0b0   << 7) | \
                /* Type */    (0b000 << 4) | \
                /* isShort */ (0b0   << 3) | \
                /* isLocal */ (0b0   << 2) | \ 
                /* topBits */ (getbyte((off << 3), 2) & 0b11) \
            )
        .byte ((off << 3) & 0xFF) | (shift & 0b111)
    .else
        .byte (\
                /* Unused */  (0b0   << 7) | \
                /* Type */    (0b000 << 4) | \
                /* isShort */ (0b1   << 3) | \
                /* isLocal */ (0b0   << 2) | \ 
                /* topBits */ (0b00) \
            )
        .halfword off << 3 | (shift & 0b111)
    .endif
.endmacro

.macro var.byte,off,scope
    .if scope != SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b001 << 4) | \
            /* isShort */ (0b0   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 2) & 0b11) \
        )
        .byte scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .elseif scope == SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b001 << 4) | \
            /* isShort */ (0b1   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 3) & 0b11) \
        )
        .halfword scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .else
        .error "Limit exceed"
    .endif
.endmacro

.macro var.short,off,scope
    .if scope != SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b010 << 4) | \
            /* isShort */ (0b0   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 2) & 0b11) \
        )
        .byte scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .elseif scope == SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b010 << 4) | \
            /* isShort */ (0b1   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 3) & 0b11) \
        )
        .halfword scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .else
        .error "Limit exceed"
    .endif
.endmacro

.macro var.int,off,scope
    .if scope != SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b011 << 4) | \
            /* isShort */ (0b0   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 2) & 0b11) \
        )
        .byte scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .elseif scope == SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b011 << 4) | \
            /* isShort */ (0b1   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 3) & 0b11) \
        )
        .halfword scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .else
        .error "Limit exceed"
    .endif
.endmacro

.macro var.ptr,off,scope
    .if scope != SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b100 << 4) | \
            /* isShort */ (0b0   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 2) & 0b11) \
        )
        .byte scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .elseif scope == SCOPE_FILE
        .byte (\
            /* Unused */  (0b0   << 7) | \
            /* Type */    (0b100 << 4) | \
            /* isShort */ (0b1   << 3) | \
            /* isLocal */ ((scope == SCOPE_LOCAL ? 0b1 : 0b0) << 2) | \ 
            /* topBits */ (getbyte(off, 3) & 0b11) \
        )
        .halfword scope == SCOPE_FILE ? off + 0x400 & 0xFFFF : off & 0xFFFF
    .else
        .error "Limit exceed"
    .endif
.endmacro

.macro RETURN
    .byte 0xF1
.endmacro

.macro EXIT
    .byte 0xF0
.endmacro

.macro STACK_CLAIM, amount
    .byte 0xF6, amount
.endmacro

.macro STACK_SIZE, amount
    .byte 0xF7
    .halfword amount
.endmacro

; calls a function
.macro syscall,value
    .byte 0xE0 | ((value >> 8) & 0xF), (value & 0xFF)
.endmacro

; Calls local subroutine
.macro call,addr,reserve
    .byte 0xF5
    .halfword addr - code_start, reserve
.endmacro

; flow statements
; absolute jump
.macro jmp,addr
    .byte 0xF2
    .halfword addr - code_start
.endmacro

; jump if pop'd value not equal zero
.macro jne,addr
    .byte 0xF3
    .halfword addr - code_start
.endmacro

; jump if pop'd value equal zero
.macro jeq,addr
    .byte 0xF4
    .halfword addr - code_start
.endmacro

; ALU-related stuff
;UNARY operators
.macro OP.POP
    .byte 0x80
.endmacro
.macro OP.POST_INC
    .byte 0x81
.endmacro
.macro OP.POST_DEC
    .byte 0x82
.endmacro
.macro OP.PRE_INC
    .byte 0x83
.endmacro
.macro OP.PRE_DEC
    .byte 0x84
.endmacro
.macro OP.COMPLIMENT
    .byte 0x85
.endmacro
.macro OP.BIT_NOT
    .byte 0x86
.endmacro
.macro OP.NOT
    .byte 0x87
.endmacro

; BINARY OPERATORS
.macro OP.INDEX
    .byte 0x88
.endmacro
.macro OP.MUL
    .byte 0x89
.endmacro
.macro OP.DIV
    .byte 0x8A
.endmacro
.macro OP.MOD
    .byte 0x8B
.endmacro
.macro OP.ADD
    .byte 0x8C
.endmacro
.macro OP.SUB
    .byte 0x8D
.endmacro
.macro OP.SLL
    .byte 0x8E
.endmacro
.macro OP.SRL
    .byte 0x8F
.endmacro
.macro OP.SGT
    .byte 0x90
.endmacro
.macro OP.SLT
    .byte 0x91
.endmacro
.macro OP.SGTE
    .byte 0x92
.endmacro
.macro OP.SLTE
    .byte 0x93
.endmacro
.macro OP.EQU
    .byte 0x94
.endmacro
.macro OP.NEQ
    .byte 0x95
.endmacro
.macro OP.BIT_AND
    .byte 0x96
.endmacro
.macro OP.BIT_XOR
    .byte 0x97
.endmacro
.macro OP.BIT_OR
    .byte 0x98
.endmacro
.macro OP.AND
    .byte 0x99
.endmacro
.macro OP.OR
    .byte 0x9A
.endmacro
.macro OP.ASSIGN
    .byte 0x9B
.endmacro

; BINARY OPERATORS WITH LOCAL VARS
.macro OP.SELF_MUL
    .byte 0x9C
.endmacro
.macro op.SELF_DIV
    .byte 0x9D
.endmacro
.macro op.SELF_MOD
    .byte 0x9E
.endmacro
.macro op.SELF_ADD
    .byte 0x9F
.endmacro
.macro op.SELF_SUB
    .byte 0xA0
.endmacro
.macro op.SELF_SLL
    .byte 0xA1
.endmacro
.macro op.SELF_SRL
    .byte 0xA2
.endmacro
.macro op.SELF_AND
    .byte 0xA3
.endmacro
.macro op.SELF_XOR
    .byte 0xA4
.endmacro
.macro op.SELF_OR
    .byte 0xA5
.endmacro

.macro add_item,id1,id2,func
    .halfword id1
    .halfword id2
    .halfword func - code_start
.endmacro

.macro save_count,start,end
    .halfword ((end - start) - 1) / 6
.endmacro

.macro makeheader,stack,main,frame
    .ascii "THEIRSCE"
    .word code_start
    .word text_start
    .word stack
    .halfword frame - code_start
    .halfword main - code_start
    .halfword section_1_start
    .halfword section_2_start
    .halfword section_3_start
    .halfword section_4_start
    .halfword section_5_start
    .halfword section_6_start
.endmacro

; Function labels
.definelabel printf,                      0x0
.definelabel set_person,                  0x5
.definelabel set_person_3d,               0x6
.definelabel set_position,                0x7
.definelabel set_position_3d,             0x8
.definelabel delete_person,               0x9
.definelabel animate_person,              0xA
.definelabel set_balloon,                 0xB
.definelabel get_param,                   0xC
.definelabel set_param,                   0xD
.definelabel move_position,               0xE
.definelabel move_position_3d,            0xF
.definelabel na_move_position,            0x10
.definelabel na_move_position_3d,         0x11
.definelabel move_check,                  0x12
.definelabel sky_init,                    0x13
.definelabel cloud_init,                  0x14
.definelabel cloud_inc_alpha,             0x15
.definelabel cloud_dec_alpha,             0x16
.definelabel delete_cloud_dec_alpha,      0x17
.definelabel trap_line,                   0x18
.definelabel trap_box,                    0x19
.definelabel trap_box_stoptimer,          0x1A
.definelabel trap_box_stoptimer_pop,      0x1B
.definelabel trap_poly4,                  0x1C
.definelabel trap_poly4_stoptimer,        0x1D
.definelabel trap_poly4_stoptimer_pop,    0x1E
.definelabel trap_line_3d,                0x1F
.definelabel trap_box_3d,                 0x20
.definelabel trap_box_stoptimer_3d,       0x21
.definelabel trap_box_stoptimer_pop_3d,   0x22
.definelabel trap_poly4_3d,               0x23
.definelabel trap_poly4_stoptimer_3d,     0x24
.definelabel trap_poly4_stoptimer_pop_3d, 0x25
.definelabel trap_contact_chr,            0x26
.definelabel delete_trap,                 0x27
.definelabel is_trap,                     0x28
.definelabel event_line,                  0x29
.definelabel event_box,                   0x2A
.definelabel event_poly4,                 0x2B
.definelabel event_line_3d,               0x2C
.definelabel event_box_3d,                0x2D
.definelabel event_poly4_3d,              0x2E
.definelabel delete_event,                0x2F
.definelabel is_event,                    0x30
.definelabel line_hit,                    0x31
.definelabel line_hit_ply,                0x32
.definelabel line_hit_npc,                0x33
.definelabel line_hit_3d,                 0x34
.definelabel line_hit_ply_3d,             0x35
.definelabel line_hit_npc_3d,             0x36
.definelabel delete_line_hit,             0x37
.definelabel is_line_hit,                 0x38
.definelabel scope,                       0x39
.definelabel scope_3d,                    0x3A
.definelabel delete_scope,                0x3B
.definelabel is_scope,                    0x3C
.definelabel scroll_direct,               0x3D
.definelabel scroll,                      0x3E
.definelabel zoom_scroll,                 0x3F
.definelabel is_scroll,                   0x40
.definelabel scroll_four,                 0x41
.definelabel fst_load,                    0x43
.definelabel gradation_palet,             0x44
.definelabel textbox,                     0x45
.definelabel event_line_inf,              0x65
.definelabel event_box_inf,               0x66
.definelabel event_poly4_inf,             0x67
.definelabel event_line_3d_inf,           0x68
.definelabel event_box_3d_inf,            0x69
.definelabel event_poly4_3d_inf,          0x6A
.definelabel scroll_cnt,                  0x70
.definelabel zoom_scroll_cnt,             0x71
.definelabel map_bright,                  0x72
.definelabel change_bg_anime,             0x73
.definelabel get_bg_anime_param,          0x74
.definelabel scope_msg,                   0x75
.definelabel scope_msg_3d,                0x76
.definelabel is_sideview,                 0x7D
.definelabel get_map_no,                  0x7E
.definelabel bg_alpha,                    0x7F
.definelabel strcmp,                      0x86
.definelabel get_sys_map_rate,            0x8F
.definelabel get_int_no,                  0x9A
.definelabel special_person,              0x9E
.definelabel special_person_3d,           0x9F
.definelabel walk_se,                     0xA4
.definelabel get_mapsize_x,               0xA5
.definelabel get_mapsize_y,               0xA6
.definelabel set_3d_zoom_rate,            0xA7
.definelabel set_cloud_h,                 0xAA
.definelabel move_stop,                   0xAB
.definelabel set_child_chr,               0xAD
.definelabel del_child_chr,               0xAE
.definelabel get_child_pos,               0xAF
.definelabel get_parent_chr,              0xB0
.definelabel is_bg_atari,                 0xB1
.definelabel set_gradation_chr,           0xB3
.definelabel set_rot_chr_color,           0xB4
.definelabel scroll_offset,               0xB5
.definelabel set_bg_pal_anime,            0xB8
.definelabel get_pl_move_spd,             0xBA
.definelabel get_pl_move_dir,             0xBB
.definelabel set_force_mode,              0xC6
.definelabel trap_force_line,             0xC7
.definelabel trap_force_box,              0xC8
.definelabel trap_force_poly4,            0xC9
.definelabel trap_force_line_3d,          0xCA
.definelabel trap_force_box_3d,           0xCB
.definelabel trap_force_poly4_3d,         0xCC
.definelabel trap_force_rain_point,       0xCD
.definelabel trap_force_chr,              0xCE
.definelabel line_hit_force,              0xCF
.definelabel line_hit_force_3d,           0xD0
.definelabel get_force_pow,               0xD1
.definelabel get_force_lever,             0xD2
.definelabel set_csp_param,               0xD3
.definelabel get_csp_param,               0xD4
.definelabel calc_csp_param,              0xD5
.definelabel set_move_pass,               0xDA
.definelabel move_pass,                   0xDB
.definelabel scroll_limit,                0xDD
.definelabel demo_stop_move_pass,         0xE2
.definelabel trap_force_rain_point_3d,    0xE5
.definelabel trap_force_rain_chr,         0xE6
.definelabel get_force_rain_trap_count,   0xE7
.definelabel get_force_rain_trap_no,      0xE8
.definelabel get_prev_crate,              0xEA
.definelabel force_obj_delete,            0xF1
.definelabel get_force_action,            0xF2
.definelabel set_chr_bright,              0xF6
.definelabel set_fade_chr_color,          0xF8
.definelabel set_line_hit_mode,           0xFB
.definelabel trap_force_box_ivy_up,       0xFF
.definelabel trap_force_box_ivy_dn,       0x100
.definelabel trap_force_poly4_ivy_up,     0x101
.definelabel trap_force_poly4_ivy_dn,     0x102
.definelabel set_ladder,                  0x104
.definelabel print_screen,                0x108
.definelabel cross_fade,                  0x109
.definelabel define_texture,              0x110
.definelabel get_ce_arg,                  0x111
.definelabel set_ce_arg,                  0x112
.definelabel set4_ce_arg,                 0x113
.definelabel set_weather_disp,            0x11C
.definelabel set_keyframe,                0x11F
.definelabel set_keyframe_arg,            0x120
.definelabel delete_keyframe,             0x121
.definelabel debug_bp,                    0x127
