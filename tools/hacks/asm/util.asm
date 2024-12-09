.expfunc get_screen_width(), int(640)
.expfunc get_screen_height(), int(224)

.expfunc to_fp16(v), int(v * 16)
.expfunc X_COORD(x), to_fp16(x)
.expfunc Y_COORD(y), to_fp16(y)
.expfunc GS_X_COORD(x), int(to_fp16(2048 - (get_screen_width()  / 2) + (x)))
.expfunc GS_Y_COORD(y), int(to_fp16(2048 - (get_screen_height() / 2) + ((y) / 2)))
