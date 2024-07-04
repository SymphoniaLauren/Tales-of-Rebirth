.ps2
.open __BTL_OVL_PATH__, 0x002EF680

.definelabel strCatKanji, 0x32C508
.definelabel getBtlStr, 0x306048

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