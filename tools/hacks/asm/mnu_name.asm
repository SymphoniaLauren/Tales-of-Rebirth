.ps2
.open "..\..\..\1_extracted\DAT\OVL\11224.ovl", "..\..\..\3_patched\patched_temp\DAT\OVL\11224.ovl", 0x02edc00

NUM_COLUMNS equ 0xD
NUM_ROWS equ 0x5

; limit keyboard draw
.org 0x002EE6B0
    slti a0, a1, NUM_COLUMNS	; num of columns
.org 0x002EE6D0
    slti a1, t0, NUM_ROWS	; num of rows

; cursor scrolling
.org 0x002EED00
    addiu v1, s0, NUM_COLUMNS	; num of columns
.org 0x002EED0C
    li v0, NUM_COLUMNS		; num of columns

; highlighting selected character
.org 0x002edf0c
    li a1, NUM_COLUMNS		; num of columns

; selected cursor click
.org 0x002eee88
    li v1, NUM_COLUMNS		; num of columns

; cursor scrolling
.org 0x002EED14
    addiu a0, s1, NUM_ROWS	; num of rows
    li v1, NUM_ROWS		; num of rows

; center cursor
.org 0x002EED8C
    sra v1, t1, 0x2		; divide width by 4
    addu a1, a1, t3
    subu t2, t2, v1		; subtract from start of cursor pos

; center typed letters
.org 0x002EE1C4
    addiu a1, s3, -0x70

; when clicking, dont mult by 2 to get correct value from string
.org 0x002EEEA0
    nop

; write one byte when clicking
.org 0x002eeec4
    sb zero, 0x1(a2)
    nop
    nop

; read one byte at a time
.org 0x002ee540
    addiu s3, a3, 0x1

; zero out second byte, skip second byte read
.org 0x002EE558
    sb zero, 0x1(a0)
    nop
    nop

;font env stuff
.org 0x002EF224
    .halfword 0xF0		; move typed letters left
.org 0x002EF240
    .halfword 0x150		; move keyboard right
    .halfword 0x200		; move keyboard down
    .halfword 0x1e0		; letter width
    .halfword 0x100		; letter height
    .halfword 0x1f0		; font width
    .halfword 0x100		; font height

; fix highlight width and start pos
;.org 0x002EE3E8
;    li a3, 0x1a0    ; new width, incr from c0

;.org 0x002EE3DC
;    addiu a1, s3, -0x70     ; move left 0x10

; screw it just nop the transform
.org 0x02ee420
    nop

.close