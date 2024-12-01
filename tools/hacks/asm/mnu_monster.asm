.ps2
.open __MNU_MONSTER_OVL_PATH__, 0x002D8900

; Use normal fonts
.org 0x2df175
    .byte 0

.org 0x02df189
    .byte 0

; Window size hack
.org 0x2DEBC4
.hword 0x6E60

.org 0x2DEBCC
.hword 0x2340

; replace name compare
.org 0x02df458
.word monster_book_name_compare
.close