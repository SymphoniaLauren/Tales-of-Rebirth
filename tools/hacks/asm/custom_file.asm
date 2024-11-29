.ps2
.createfile "..\..\..\3_patched\patched_temp\DAT\BIN\10227.bin", 0x04CD500

.asciiz "Hello world from a custom file!"

; Set this to 1 to enable debug mode
DEBUG_MODE:
.halfword 0
; Set this to 1 to see all voice clips in debug
; Set this to 0 to only see clips NOT in char/cat ids 1 thru 6
VERBOSE_MODE:
.halfword 0

.func draw_sub_wrapper
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    jal 0x00306478  ; repeat
    nop
    jal draw_subs
    nop
    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

;.func CallBtlVoiceWrapper
    ; a0 = fontenv
	;addiu sp, sp, -0x10
	;sw ra, 0xc(sp)
    ;sw s0, 0x8(sp)
    ;sw s1, 0x4(sp)
    
    ;jal setup_text
    ;nop

    ;lw s0, 0x8(sp)
    ;lw s1, 0x4(sp)
    ;lw a1,0x440(s1)
    ;lw ra, 0xc(sp)
	;jr ra
	;addiu sp, sp, 0x10
;.endfunc

.func endBattle_wrapper
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    
    jal clear_subs
    nop

    jal 0x002f2650   ; endBattle
    nop

    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

.func playAbsVoice_wrapper
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    
    jal 0x018c610   ; repeat
    nop

    jal clear_subs
    nop

    li a0, 0
    jal setup_text      ; register the text with no btl chr struct
    move a1, s0

    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

.func registBtlChrVoice_wrapper
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    sw s0, 0x8(sp)
    sw s1, 0x4(sp)
    
    move s0, a0
    jal 0x0032fae0      ; registBtlChrVoice
    move s1, a1

    move a0, s0
    jal setup_text
    move a1, s1

    lw s0, 0x8(sp)
    lw s1, 0x4(sp)
    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

.func add_skit_line_hook
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    
    jal fntenv_make_default
    nop

    jal process_skit_line
    ; get text pointer back
    lw a0, 0x5c(s0)

    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

.func move_skit_prompt
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    sw s0, 0x8(sp)

    li s0, 0x2b2008 
    lw s0, 0x0(s0)

    beq s0, zero, @@end
    li v1, 0x8660   ; original
    li v1, 0x8500   ; new, if beq not zero
@@end:
    lw s0, 0x8(sp)
    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

.func clear_skit_hook
	addiu sp, sp, -0x10
	sw ra, 0xc(sp)
    
    jal clear_skit
    nop

    jal 0x0013feb0  ; repeat, clears out skit data
    nop

    lw ra, 0xc(sp)
	jr ra
	addiu sp, sp, 0x10
.endfunc

.importobj "./build/hack.o"
.importobj "./build/battle_subs.o"

.close