.ps2
.open __3DFIELD_OVL_PATH__, 0x002EF680

; Double box size
.org 0x2F1780
	li a3, 0x1D0

;Change height of Box:
.org 0x317E84
    li a0, 0x7F40

; Area Vertical pos
.org 0x317FE0
	li a2, 0x7F80

; Keeps area text centered
.org 0x317FE4
    nop

; Routine to center the area type text
.org 0x31801C
    lhu a1, 0xD2(sp)

.org 0x318024
    jal custom_code
	lw	a0,0x69AC(fp)

; end of rodata
.org 0x31EAB4
    custom_code:
    li t3, 0xA00
    subu t3, a1
    sra t3, 0x1
    lw v1, 0xE4(sp)
    addu a1, t3, v1
    jr ra
    nop
.close