.ps2
.open __SLPS_PATH__, 0x00FF000
;credits to Ethanol (he's the man) and SymphoniaLauren

.definelabel gPartyData, 0x232D80
gPartyData_size equ 0x3A94
.definelabel gVMData, 0x246000
gVMData_size equ 0x400
.definelabel alloc_EE, 0x109500
.definelabel free_EE, 0x109538
.definelabel blk_memcpy, 0x108F20
.definelabel memset, 0x1BFC34

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

.org 0x1CF680
;Shoves font blob into the exe (I'M SORRY KAJI)
    .incbin "fonttiles.bin"

.org 0x1CA240
;ASCII width table
; Char         | L  | R
/* ０ */ .byte   05 , 05
/* １ */ .byte   06 , 05
/* ２ */ .byte   05 , 05
/* ３ */ .byte   05 , 06
/* ４ */ .byte   04 , 07
/* ５ */ .byte   06 , 06
/* ６ */ .byte   06 , 06
/* ７ */ .byte   06 , 07
/* ８ */ .byte   04 , 05
/* ９ */ .byte   04 , 04
/* Ａ */ .byte   04 , 06
/* Ｂ */ .byte   05 , 06
/* Ｃ */ .byte   05 , 06
/* Ｄ */ .byte   05 , 06
/* Ｅ */ .byte   05 , 07
/* Ｆ */ .byte   05 , 08
/* Ｇ */ .byte   05 , 07
/* Ｈ */ .byte   05 , 07
/* Ｉ */ .byte   08 , 09
/* Ｊ */ .byte   07 , 08
/* Ｋ */ .byte   05 , 06
/* Ｌ */ .byte   05 , 08
/* Ｍ */ .byte   05 , 05
/* Ｎ */ .byte   05 , 06
/* Ｏ */ .byte   05 , 05
/* Ｐ */ .byte   05 , 06
/* Ｑ */ .byte   05 , 05
/* Ｒ */ .byte   05 , 07
/* Ｓ */ .byte   06 , 07
/* Ｔ */ .byte   05 , 07
/* Ｕ */ .byte   05 , 06
/* Ｖ */ .byte   05 , 06
/* Ｗ */ .byte   05 , 03
/* Ｘ */ .byte   05 , 07
/* Ｙ */ .byte   05 , 08
/* Ｚ */ .byte   05 , 05
/* ａ */ .byte   06 , 08
/* ｂ */ .byte   06 , 07
/* ｃ */ .byte   07 , 08
/* ｄ */ .byte   06 , 07
/* ｅ */ .byte   06 , 07
/* ｆ */ .byte   07 , 09
/* ｇ */ .byte   06 , 07
/* ｈ */ .byte   06 , 07
/* ｉ */ .byte   08 , 09
/* ｊ */ .byte   09 , 10
/* ｋ */ .byte   05 , 07
/* ｌ */ .byte   09 , 09
/* ｍ */ .byte   03 , 05
/* ｎ */ .byte   06 , 07
/* ｏ */ .byte   06 , 07
/* ｐ */ .byte   06 , 07
/* ｑ */ .byte   06 , 07
/* ｒ */ .byte   07 , 09
/* ｓ */ .byte   07 , 08
/* ｔ */ .byte   07 , 08
/* ｕ */ .byte   06 , 07
/* ｖ */ .byte   05 , 07
/* ｗ */ .byte   03 , 04
/* ｘ */ .byte   06 , 08
/* ｙ */ .byte   05 , 07
/* ｚ */ .byte   06 , 07
/* ， */ .byte   01 , 15
/* ． */ .byte   01 , 15
/* ・ */ .byte   06 , 08
/* ： */ .byte   08 , 08
/* ； */ .byte   07 , 08
/* ？ */ .byte   04 , 05
/* ！ */ .byte   07 , 09
/* ／ */ .byte   00 , 01
/* （ */ .byte   12 , 01
/* ） */ .byte   01 , 13
/* ［ */ .byte   13 , 01
/* ］ */ .byte   01 , 11
/* ｛ */ .byte   14 , 01
/* ｝ */ .byte   01 , 14
/* ＋ */ .byte   03 , 06
/* － */ .byte   06 , 07
/* ＝ */ .byte   04 , 03
/* ＜ */ .byte   03 , 03
/* ＞ */ .byte   03 , 03
/* ％ */ .byte   02 , 09
/* ＃ */ .byte   04 , 04
/* ＆ */ .byte   02 , 04
/* ＊ */ .byte   04 , 04
/* ＠ */ .byte   00 , 01
/* ｜ */ .byte   08 , 08
/*  ” */ .byte   01 , 15
/*  ’ */ .byte   01 , 18
/* ＾ */ .byte   07 , 06
/* 「 */ .byte   10 , 01
/* 」 */ .byte   01 , 11
/* 〜 */ .byte   05 , 06
/* ＿ */ .byte   00 , 00
/* 、 */ .byte   00 , 13
/* 。 */ .byte   01 , 12

.org 0x1CA518
;em dash width
    .byte 01, 01

;use debug death notice
.org 0x1282A0
    nop

.close