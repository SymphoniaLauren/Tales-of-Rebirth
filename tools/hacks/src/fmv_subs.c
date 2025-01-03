#include "types.h"
#include "fmv_subs.h"
#include "sceio.h"
#include "rebirth.h"
#include "fmv_subs_text.h"

DATA int frame_counter = 0;
DATA int sub_index = 0;
DATA int sub_count = 0;
DATA const fmv_sub *current_subs;
DATA fontenv_struct fnt_env;
DATA credit_line current_line;
DATA u8 sub_offset = 0;

void draw_line(int arg0);
void populate_screen(const fmv_sub *sub);
void fntenv_make_default(fontenv_struct *);
int count_lines(const char *);
extern void fontenv_draw_centered(fontenv_struct *, const char *);
extern void write_register(u32, u64);
extern void func_00104F50(fontenv_struct *, u16, u16);
extern void func_00104F60(fontenv_struct *, u16, u16);
extern void func_00104F70(fontenv_struct *, u32);
extern void func_00104F78(fontenv_struct *, u16, u16);
extern void get_str_width(fontenv_struct *, const char *, u16 *, u16 *);
extern void fontenv_set_palette(fontenv_struct *, int, int);

int update_sub_callback(void)
{
    // remove callbacks so the fmv will resume upon termination
    if (sub_index == sub_count)
    {
        gMain.fmv_info.callback_0 = NULL;
        gMain.fmv_info.callback_1 = NULL;
    }
    else
    {
        frame_counter++;
        if (current_subs[sub_index + 1].start_frame <= frame_counter)
        {
            sub_index++;
            populate_screen(&current_subs[sub_index]);
        }
    }

    return 0;
}

void draw_text_callback(int param_1)
{
    write_register(SCE_GS_TEX1_1, SCE_GS_SET_TEX1_1(0, 0, 1, 1, 0, 0, 0));
    write_register(SCE_GS_TEST_1, SCE_GS_SET_TEST_1(1, 1, 0, 0, 0, 0, 1, 1));
    write_register(SCE_GS_ALPHA_1, SCE_GS_SET_ALPHA_1(0, 1, 0, 1, 0));
    write_register(SCE_GS_CLAMP_1, SCE_GS_SET_CLAMP_1(2, 2, 0, SCREEN_WIDTH - 1, 0, (SCREEN_HEIGHT * 2) - 1));
    ((unkspad *)SCRATCHPAD_ADDR)->unk110 = param_1;
    draw_line(param_1);
}

void populate_screen(const fmv_sub *sub)
{
    u16 width;
    u16 height;
    char *text;

    memset(&current_line, 0x0, sizeof(credit_line));
    fntenv_make_default(&fnt_env);
    func_00104F50(&fnt_env, 0x1a0, 0xd0);

    if (sub->text != NULL)
    {
        int lines = count_lines(sub->text);
        func_00104F78(&fnt_env, 0x100, 0xE0);
        get_str_width(&fnt_env, sub->text, &width, &height);
        current_line.text = sub->text;
        current_line.color = 7;
        current_line.x = GS_X_COORD((SCREEN_WIDTH / 2)) - (width / 2);
        if (lines == 1)
        {
            current_line.y = GS_Y_COORD(404 + sub_offset);
        }
        else
        {
            current_line.y = GS_Y_COORD(393 + sub_offset);
        }
    }
}

int count_lines(const char *str)
{
    int lines = 1;
    u8 chr;
    // shitty loop thru text until we find 01
    for (; (chr = str[0]) != 0; str++)
    {
        // check for command chars 4 thru f
        if (chr >= 0x4 && chr <= 0xf)
        {
            // if find one, ignore next 4 bytes
            str += 5;
        }
        else if (chr == 0x01)
        {
            lines = 2;
        }
    }
    return lines;
}

void draw_line(int arg0)
{
    fntenv_make_default(&fnt_env);
    func_00104F50(&fnt_env, 0x1a0, 0xd0);
    func_00104F70(&fnt_env, arg0);

    if (current_line.text != NULL)
    {
        fontenv_set_palette(&fnt_env, current_line.color, 0x80);
        func_00104F78(&fnt_env, 0x100, 0xE0);
        func_00104F60(&fnt_env, current_line.x, current_line.y);
        fontenv_draw_centered(&fnt_env, current_line.text);
        // draw_string(&fnt_env, current_line.text);
    }
}

void init_fmv_subs()
{
    const fmv_entry *fmv;
    int fmv_id;
    printf("Playing fmv -> %d - Flags -> %x\n", gMain.fmv_info.fmv_id, gMain.fmv_info.flags);

    frame_counter = 0;
    current_line.text = NULL;
    sub_index = 0;

    fmv_id = gMain.fmv_info.fmv_id - 17;

    if (fmv_id < 0 || fmv_id > 3)
    {
        return;
    }

    // Hack for the speech cutscene which has lower black bars
    if (fmv_id == 0)
    {
        sub_offset = 7;
    }
    else
    {
        sub_offset = 0;
    }

    fmv = &fmv_table[fmv_id];

    gMain.fmv_info.callback_0 = &update_sub_callback;
    gMain.fmv_info.callback_1 = &draw_text_callback;
    sub_count = fmv->sub_count - 1;
    current_subs = fmv->subs;
    return;
}
