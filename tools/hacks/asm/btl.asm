.ps2
.open __BTL_OVL_PATH__, 0x002EF680

.definelabel strCatKanji, 0x32C508
.definelabel getBtlStr, 0x306048

; Replace printBtlEnemyStatusDisp
.org 0x300150
    j  printBtlEnemyStatusDisp
    nop

.org 0x300220
    li    a1, 0

; BATTLE SUBS
.org 0x002f1adc
    jal draw_sub_wrapper    ; in battle main loop to draw subs

.org 0x0032f8e0
    ;sd ra, 0x0(sp)      ; repeat, moved instruction up so we have space to jal
    ;jal CallBtlVoiceWrapper     ; need to repeat lw a1,0x440(s1) inside function
    ;sq s5,0x10(sp)      ; repeat   
    ; replaced with calling from directly inside registBtlChrVoice's below

.org 0x0032ef6c
    jal registBtlChrVoice_wrapper

.org 0x0032fa24
    jal registBtlChrVoice_wrapper

.org 0x0032fa84
    jal registBtlChrVoice_wrapper

.org 0x002ef890
    jal endBattle_wrapper

.org 0x0032F610
    jal playAbsVoice_wrapper

; move post battle stuff around
; move ENHANCE EXECUTABLE! down
.org 0x002FD444
    ori v0, zero, GS_Y_COORD(448)

; move the blue background for ENHANCE EXECUTABLE! down
.org 0x002fd374 
    ori v1, zero, GS_Y_COORD(448)

; move item window down a bit to give space for subs
.org 0x0032d4e0 
    ori a0, zero, y_coord(174)
    ;ori a0, zero, y_coord(154)    ; orig y_coord(166)

; move around the params for を習得
.org 0x032C044
    li         a0,0x5F

.org 0x032C05C
    li         a0,0x5F

.org 0x032C080
    li         a0,0x63

; move around the params for を料理しました。
; Be careful about changing the amount of instructions
.org 0x32C278
    addiu      sp,sp,-0xf0
    sq         s5,0x90(sp)
    sq         s0,0xe0(sp)
    sq         s1,0xd0(sp)
    sq         s2,0xc0(sp)
    sq         s3,0xb0(sp)
    sq         s4,0xa0(sp)
    sd         ra,0x80(sp)
    lui        v0,0x35
    move       s5,v0
    ori        v1,zero,0x8000
    addiu      v0,v0,-0x4700
    addu       s0,v0,v1
    jal        getBtlStr
    li         a0,0x62
    sw         zero,0x0(sp)
    move       a1,v0
    jal        strCatKanji
    move       a0,sp
    lw         a1,0x7EA0(s5)
    beq        a1,zero,0x32C4E0
    nop
    jal        strCatKanji
    move       a0,sp
    nop

;Walto WORDSWORDSWORDS fix (Credit Julian)
.org 0x2f2208
    li         a3, 0xC8

.close