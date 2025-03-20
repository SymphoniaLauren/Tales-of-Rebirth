.ps2
.open __SLPS_PATH__, 0x00FF000
;credits to Ethanol (he's the man) and SymphoniaLauren

; .definelabel gPartyData, 0x232D80
; gPartyData_size equ 0x3A94
; .definelabel gVMData, 0x246000
; gVMData_size equ 0x400
; .definelabel alloc_EE, 0x109500
; .definelabel free_EE, 0x109538
; .definelabel blk_memcpy, 0x108F20
; .definelabel memset, 0x1BFC34

; Menu background fix (For emulator)
.org 0x173B6C :: li t1,0x1

; Move text palette to new index so it
; isn't corrupted by element icons palettes
.org 0x1088a4 :: addiu a0, v0, 0x16
.org 0x1088c0 :: addiu a1, v0, 0x16

; Increase text limit
.org 0x0020982C :: .word 0x180

; Let's create a permanent pocket of data for
; the insatiable mnu_monster file text

; original value -> 0x00391400
.definelabel __heap_start, 0x003A0000
.definelabel __heap_ptr, 0x0020E448

; Repoint __heap_start symbol to be later
.org 0x001001D0 :: lui        a0,hi(__heap_start)
.org 0x001001D8 :: addiu      a0,a0,lo(__heap_start)

; Repoint malloc base
.org __heap_ptr :: .word __heap_start

; Repoint memory manage alloc size
.org 0x0010BC10 :: lui        a0,hi(__heap_start)
.org 0x0010BC1C :: addiu      a0,a0,lo(__heap_start)


.include "glue.asm"

; Replace init function
.org 0x00101EA8
.area 0x001024C8-., 0x00
.importobj "./build/init.o"
.endarea

.org 0x001378A0
    j        fmv_hijack
    nop

.org 0x00100248
    jal      init_all_the_things ; defined in init.o

; Enable dummied out debug print call
.org 0x0010d380
    j        printf
    nop

; alloc more image mem for palettes
;.org 0x1045fc
;    li a1,0x80
;    li a2,0x80

.org 0x122F98
    j extra_syscall
    lhu        v1,0x40(sp)
    ;addiu      a0,a0,0x5300
    syscall_back:

.org 0x123010
syscall_call:

;.org 0x211E98
.org 0x231028
/*
party_data_save:
.word 0
vm_data_save:
.word 0
 */
extra_syscall:
    sw v0,0x1038(a1)
    /*
    addiu      sp,sp,-0x50
    sq         a0,0(sp)
    sq         a1,0x10(sp)
    sq         a2,0x20(sp)
    sq         a3,0x30(sp)
    sq         v0,0x40(sp)
     */
    beq v1,0x145,EventReplayInfoSave
    nop
    beq v1,0x146,EventReplayResumeSave
    nop
    b extra_syscall_ret
    nop
EventReplayInfoSave:
EventReplayResumeSave:
    j          syscall_call
    li         v0,0

    ; as the machinery is not there in the
    ; rsce files this code is useless
/*
    li       a0,gPartyData_size
    li       a1,1 ; from_bottom
    jal      alloc_EE
    li       a2,0x40

    li       at, party_data_save
    sw       v0, 0(at)

    move     a0, v0
    li       a1, gPartyData
    jal      blk_memcpy
    li       a2, gPartyData_size

    li       at, gPartyData
    lw       a0, 0x3310(at)
    li       v0, 0xffffffef
    and      a0,a0,v0
    sw       a0, 0x3310(at)

    li       a0,gVMData_size
    li       a1,1 ; from_bottom
    jal      alloc_EE
    li       a2,0x40
    li       at, vm_data_save
    sw       v0, 0(at)

    move     a0, v0
    li       a1, gVMData
    jal      blk_memcpy
    li       a2, gVMData_size

    li       a0,gVMData
    li       a1,0
    jal      memset
    li       a2,0x100

    b        extra_syscall_end
    nop

EventReplayResumeSave:
    li       at, party_data_save
    li       a0, gPartyData
    move     a1, at
    jal      blk_memcpy
    li       a2, gPartyData_size

    li       at, party_data_save
    lw       a0, 0(at)
    jal      free_EE
    sw       zero, 0(at)

    li       at, vm_data_save
    li       a0, gVMData
    move     a1, at
    jal      blk_memcpy
    li       a2, gVMData_size


    li       at, vm_data_save
    lw       a0, 0(at)
    jal      free_EE
    sw       zero, 0(at)

extra_syscall_end:
    lq         a0,0(sp)
    lq         a1,0x10(sp)
    lq         a2,0x20(sp)
    lq         a3,0x30(sp)
    li         v0,0
    j          syscall_call
    addiu      sp,sp,0x50
 */

extra_syscall_ret:
    j          syscall_back
    addiu      a0,a0,0x5300
    ;addiu      sp,sp,0x50


; No smooshy (we don't like smooshy)
.org 0x105E18
    li   v0, 0x1

;Synopsis linebreak fixes by Julian
.org 0x108C0C
	nop
	nop

.org 0x108D14
	nop
	nop

; monospace on +items
.org 0x0016AD34 
    nop
.org 0x0016ad48
    nop

; Hooks for skit centering
.org 0x0013E114
    jal add_skit_line_hook

.org 0x0013e2e4
    jal draw_skit

; Move skit prompt up
.org 0x0012b7cc
    jal move_skit_prompt

;Cutscene Text Var Width fix
.org 0x11CC60
;sets bool flag for ascii to 0
    ori  s4, zero, 0x0


.org 0x11D494
;skips stright to the good stuff
    b    0x0011D4A4

.org 0x175984
;Prevents some font memes in the Synopsis
	nop

;Prevents funny font with Magical Pot
.org 0x136144
    li    a1, 0x0

;Prevent funny font in Farm Fresh Groceries
.org 0x136588
    li   a1, 0x0

;Use sexier font for numbers in Farm Fresh Groceries
.org 0x1365b8
    li   a1, 0x1

;Don't monospace number in Magical Pot
;window in Farm Fresh Groceries
.org 0x136ce4
    li   a1, 0x0

;Use sexier font for numbers in Magical Pot
;window in Farm Fresh Groceries
.org 0x136d14
    li   a1, 0x1

;adjusting the whitespace lenght 
;base is 12 pixel aka /2 the lenght of monospace
; Menu text and char names whitespace
.org 0x105ea0
srl s2,s2,2

; Story text whitespace
.org 0x11d508
srl a3,s0,1

; Item name (concat) whitespace
.org 0x105f3c
srl s1,s2,0x01

; Fix semicolon that showed up as colon
.org 0x1ca1b5
.byte 0x84

.org 0x1C9D34
;for our shiny new element icons
/* Earth */ .byte 0x18, 0x00, 0x40, 0x00, 0x18, 0x18, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00
/* Wind */  .byte 0x30, 0x00, 0x40, 0x00, 0x18, 0x18, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00
/* Fire */  .byte 0x48, 0x00, 0x40, 0x00, 0x18, 0x18, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00

.org 0x1C9D64
/* Water */ .byte 0x60, 0x00, 0x40, 0x00, 0x18, 0x18, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00
/* Light */ .byte 0x78, 0x00, 0x40, 0x00, 0x18, 0x18, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00
/* Dark */  .byte 0x90, 0x00, 0x40, 0x00, 0x18, 0x18, 0x15, 0x00, 0x00, 0x00, 0x00, 0x00

.org 0x1CF680
;Shoves font blob into the exe (I'M SORRY KAJI)
    .incbin "../assets/fonttiles.bin"

.org 0x1CA240
;ASCII width table
; Char         | L  | R
/* ０ */ .byte   05 , 06
/* １ */ .byte   06 , 08
/* ２ */ .byte   06 , 07
/* ３ */ .byte   06 , 07
/* ４ */ .byte   05 , 06
/* ５ */ .byte   06 , 06
/* ６ */ .byte   06 , 06
/* ７ */ .byte   06 , 07
/* ８ */ .byte   06 , 06
/* ９ */ .byte   06 , 06
/* Ａ */ .byte   04 , 06
/* Ｂ */ .byte   06 , 06
/* Ｃ */ .byte   06 , 06
/* Ｄ */ .byte   05 , 06
/* Ｅ */ .byte   06 , 07
/* Ｆ */ .byte   06 , 08
/* Ｇ */ .byte   05 , 07
/* Ｈ */ .byte   05 , 07
/* Ｉ */ .byte   08 , 09
/* Ｊ */ .byte   07 , 08
/* Ｋ */ .byte   06 , 06
/* Ｌ */ .byte   07 , 08
/* Ｍ */ .byte   05 , 05
/* Ｎ */ .byte   05 , 06
/* Ｏ */ .byte   05 , 05
/* Ｐ */ .byte   06 , 06
/* Ｑ */ .byte   05 , 05
/* Ｒ */ .byte   05 , 07
/* Ｓ */ .byte   06 , 07
/* Ｔ */ .byte   06 , 07
/* Ｕ */ .byte   05 , 06
/* Ｖ */ .byte   05 , 06
/* Ｗ */ .byte   03 , 03
/* Ｘ */ .byte   05 , 07
/* Ｙ */ .byte   05 , 08
/* Ｚ */ .byte   06 , 07
/* ａ */ .byte   06 , 07
/* ｂ */ .byte   06 , 07
/* ｃ */ .byte   07 , 08
/* ｄ */ .byte   06 , 07
/* ｅ */ .byte   06 , 07
/* ｆ */ .byte   07 , 09
/* ｇ */ .byte   06 , 07
/* ｈ */ .byte   06 , 07
/* ｉ */ .byte   09 , 09
/* ｊ */ .byte   09 , 10
/* ｋ */ .byte   06 , 07
/* ｌ */ .byte   09 , 09
/* ｍ */ .byte   03 , 05
/* ｎ */ .byte   06 , 07
/* ｏ */ .byte   06 , 07
/* ｐ */ .byte   06 , 07
/* ｑ */ .byte   06 , 07
/* ｒ */ .byte   07 , 08
/* ｓ */ .byte   07 , 08
/* ｔ */ .byte   08 , 08
/* ｕ */ .byte   06 , 07
/* ｖ */ .byte   05 , 07
/* ｗ */ .byte   04 , 04
/* ｘ */ .byte   07 , 07
/* ｙ */ .byte   06 , 07
/* ｚ */ .byte   06 , 08
/* ， */ .byte   01 , 15
/* ． */ .byte   01 , 15
/* ・ */ .byte   08 , 08
/* ： */ .byte   09 , 09
/* ； */ .byte   08 , 09
/* ？ */ .byte   07 , 07
/* ！ */ .byte   09 , 09
/* ／ */ .byte   06 , 07
/* （ */ .byte   12 , 01
/* ） */ .byte   01 , 13
/* ［ */ .byte   13 , 01
/* ］ */ .byte   01 , 11
/* ｛ */ .byte   14 , 01
/* ｝ */ .byte   01 , 14
/* ＋ */ .byte   05 , 06
/* － */ .byte   08 , 07
/* ＝ */ .byte   04 , 03
/* ＜ */ .byte   03 , 03
/* ＞ */ .byte   03 , 03
/* ％ */ .byte   03 , 04
/* ＃ */ .byte   04 , 04
/* ＆ */ .byte   05 , 04
/* ＊ */ .byte   06 , 08
/* ＠ */ .byte   00 , 01
/* ｜ */ .byte   08 , 08
/*  ” */ .byte   01 , 15
/*  ’ */ .byte   01 , 18
/* ＾ */ .byte   07 , 06
/* 「 */ .byte   10 , 01
/* 」 */ .byte   01 , 11
/* 〜 */ .byte   05 , 06
/* ＿ */ .byte   05 , 06
/* 、 */ .byte   00 , 13
/* 。 */ .byte   01 , 12

.org 0x1CA518
;em dash width
    .byte 01, 01

;use debug death notice
.org 0x128320
    li a2,0
.org 0x12832c
    li a2,1
.org 0x128360
    li a2,2
.org 0x128354
    li a2,3
.org 0x12838c
    nop
.org 0x128364
    b 0x1282a8
    nop
.org 0x128334
    b 0x1282a8
    nop
.org 0x1282ac
    sll v0,a2,2


;apple gel sellprice fix
.orga 0x106dd4
.byte 0x19


.close