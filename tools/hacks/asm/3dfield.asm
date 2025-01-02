.ps2
.open __3DFIELD_OVL_PATH__, 0x002EF680

; Fix anikamal load bug (from original game)
.org 0x2F196C :: li a1, 0x1

; Double box size
.org 0x2F1780
	li a3, 0x1D0

;Change height of Box:
.org 0x317E84
    li a0, 0x7F40

;Get length from REAL string instead of FAKE string reeeee
.org 0x317FC0
    lw v1, 0x6988(fp)
    lw v0, 0x220(v1)
    addiu a2, sp, 0xD2
    dmove a3, zero
    jal 0x104A48
    lw a1, 0xBC(v0)
    lhu v1, 0xD2(sp)
    li s0, 0xA00
    lhu v0, 0xD0(sp)
    li a2, 0x7F80


;old fix kept for refrence sake

; Area Vertical pos
;.org 0x317FE0
;	li a2, 0x7F80

; Keeps area text centered
;.org 0x317FE4
;    nop

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