.ps2
.open __MNU_MONSTER_OVL_PATH__, 0x002D8900


; Window size hack
.org 0x2DEBC4
.hword 0x6E60

.org 0x2DEBCC
.hword 0x2340

; replace name compare
.org 0x02df458
.word monster_book_name_compare
.close