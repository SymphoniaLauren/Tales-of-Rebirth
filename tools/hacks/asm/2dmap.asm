.ps2
.open "..\..\..\3_patched\patched_temp\DAT\PAK3\00013\0001.bin", 0x002EF680

.org 0x2ef814
j    map2d_hijack
nop

; debug flag
.org 0x389b94
.byte 1

.org 0x300fa8
nop

.close