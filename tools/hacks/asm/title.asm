.ps2
.open "..\..\..\3_patched\patched_temp\DAT\OVL\00017.ovl", 0x02ef680

.org 0x02f11b0
    jal write_title_strings
    nop

.close