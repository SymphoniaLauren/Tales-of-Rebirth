.ps2
.open __BTL_OVL_PATH__, 0x002EF680

; move around the params for を習得
.org 0x032C084
    move      a0,v0

.org 0x032C08C
    move      a1,sp

; move around the params for を料理しました。
.org 0x032C2D0
    move      a0,v0

.org 0x032C2D8
    move      a1,sp

.close