.ps2
.open "..\..\1_extracted\DAT\OVL\11216.ovl", "..\..\3_patched\patched_temp\DAT\OVL\11216.ovl", 0x2d8900

; change max number of characters allowed to type in character rename
.org 0x002D8DE8
    li t0, 0xC

.close