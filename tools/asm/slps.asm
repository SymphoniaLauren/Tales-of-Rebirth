.ps2
.open __SLPS_PATH__, 0x00FF000
;credits to Ethanol (he's the man) and SymphoniaLauren

; No smooshy (we don't like smooshy)
.org 0x105E18
    li   v0, 0x1

;Cutscene Text Var Width fix
.org 0x11CC60
;sets bool flag for ascii to 0
    ori  s4, zero, 0x0


.org 0x11D494
;skips stright to the good stuff
    b    0x0011D4A4

.org 0x1CF680
;Shoves font blob into the exe (I'M SORRY KAJI)
    .incbin "fonttiles.bin"

.org 0x1CA240
;ASCII width table
; Char         | L  | R
/* ０ */ .byte   05 , 05
/* １ */ .byte   06 , 05
/* ２ */ .byte   05 , 05
/* ３ */ .byte   05 , 06
/* ４ */ .byte   04 , 07
/* ５ */ .byte   06 , 06
/* ６ */ .byte   06 , 06
/* ７ */ .byte   06 , 07
/* ８ */ .byte   04 , 05
/* ９ */ .byte   04 , 04
/* Ａ */ .byte   04 , 06
/* Ｂ */ .byte   05 , 06
/* Ｃ */ .byte   05 , 06
/* Ｄ */ .byte   05 , 06
/* Ｅ */ .byte   05 , 07
/* Ｆ */ .byte   05 , 08
/* Ｇ */ .byte   05 , 07
/* Ｈ */ .byte   05 , 07
/* Ｉ */ .byte   08 , 09
/* Ｊ */ .byte   07 , 08
/* Ｋ */ .byte   05 , 06
/* Ｌ */ .byte   05 , 08
/* Ｍ */ .byte   05 , 05
/* Ｎ */ .byte   05 , 06
/* Ｏ */ .byte   05 , 05
/* Ｐ */ .byte   05 , 06
/* Ｑ */ .byte   05 , 05
/* Ｒ */ .byte   05 , 07
/* Ｓ */ .byte   06 , 07
/* Ｔ */ .byte   05 , 07
/* Ｕ */ .byte   05 , 06
/* Ｖ */ .byte   05 , 06
/* Ｗ */ .byte   05 , 03
/* Ｘ */ .byte   05 , 07
/* Ｙ */ .byte   05 , 08
/* Ｚ */ .byte   05 , 05
/* ａ */ .byte   06 , 08
/* ｂ */ .byte   06 , 07
/* ｃ */ .byte   07 , 08
/* ｄ */ .byte   06 , 07
/* ｅ */ .byte   06 , 07
/* ｆ */ .byte   07 , 09
/* ｇ */ .byte   06 , 07
/* ｈ */ .byte   06 , 07
/* ｉ */ .byte   08 , 09
/* ｊ */ .byte   09 , 10
/* ｋ */ .byte   05 , 07
/* ｌ */ .byte   09 , 09
/* ｍ */ .byte   03 , 05
/* ｎ */ .byte   06 , 07
/* ｏ */ .byte   06 , 07
/* ｐ */ .byte   06 , 07
/* ｑ */ .byte   06 , 07
/* ｒ */ .byte   07 , 09
/* ｓ */ .byte   07 , 08
/* ｔ */ .byte   07 , 08
/* ｕ */ .byte   06 , 07
/* ｖ */ .byte   05 , 07
/* ｗ */ .byte   03 , 04
/* ｘ */ .byte   06 , 08
/* ｙ */ .byte   05 , 07
/* ｚ */ .byte   06 , 07
/* ， */ .byte   01 , 15
/* ． */ .byte   01 , 15
/* ・ */ .byte   06 , 08
/* ： */ .byte   08 , 08
/* ； */ .byte   07 , 08
/* ？ */ .byte   04 , 05
/* ！ */ .byte   07 , 09
/* ／ */ .byte   00 , 01
/* （ */ .byte   12 , 01
/* ） */ .byte   01 , 13
/* ［ */ .byte   13 , 01
/* ］ */ .byte   01 , 11
/* ｛ */ .byte   14 , 01
/* ｝ */ .byte   01 , 14
/* ＋ */ .byte   03 , 06
/* － */ .byte   06 , 07
/* ＝ */ .byte   04 , 03
/* ＜ */ .byte   03 , 03
/* ＞ */ .byte   03 , 03
/* ％ */ .byte   02 , 09
/* ＃ */ .byte   04 , 04
/* ＆ */ .byte   02 , 04
/* ＊ */ .byte   04 , 04
/* ＠ */ .byte   00 , 01
/* ｜ */ .byte   08 , 08
/*  ” */ .byte   01 , 15
/*  ’ */ .byte   01 , 18
/* ＾ */ .byte   07 , 06
/* 「 */ .byte   10 , 01
/* 」 */ .byte   01 , 11
/* 〜 */ .byte   05 , 06
/* ＿ */ .byte   00 , 00
/* 、 */ .byte   00 , 13
/* 。 */ .byte   01 , 12


.close