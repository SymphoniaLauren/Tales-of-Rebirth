#include "types.h"
#include "rebirth.h"
#include "Externs.h"
#include "Sub_Types.h"
#include "battle_subs_text.h"
#include "battle_subs.h"

#define TITLE_LINE_1 "Life Bottle Productions ver 0.9"
#ifndef PATCH_SERIAL
#define TITLE_LINE_2 "Patch serial: 0000000000"
#else
#define EXP_Q(str) _STR(str)
#define TITLE_LINE_2 "Patch serial: " EXP_Q(PATCH_SERIAL)
#endif

#define DEBUG_X GS_X_COORD(16)		// debug x
#define DEBUG_Y GS_Y_COORD(4)		// debug y
#define LINE_Y_ABOVE_UI GS_Y_COORD(316)	// y for type 1
#define LINE_Y_BEHIND_UI GS_Y_COORD(400)	// y for type 2
#define LINE_Y_POSTBATTLE_BASE GS_Y_COORD(316)	// y for type 3
#define NUM_VOICE_QUEUES 6			// slots to hold active/pending voice data, 6 is fine
#define NUM_TEXT_CONTAINERS 2		// number of active sub lines - may need to adj code if increasing
#define POST_FRAME_COUNT 20			// number of frames for fade out animation

extern "C"
{
	extern void func_00104F30(fontenv_unk2*);
	extern char* func_00105568(fontenv_struct*, fontenv_unk1*, char*);
	extern char* func_001052F0(fontenv_struct*, fontenv_unk1*, char*);
	extern char* func_00105030(fontenv_struct*, fontenv_unk1*, fontenv_unk2*, char*);
	extern char* fontenv_render(fontenv_struct*, fontenv_unk1*);
	extern char* func_00105268(fontenv_struct*, fontenv_struct*, char*);
	void fontenv_draw_centered(fontenv_struct*, char*);
	DATA fontenv_struct fontenv;
	DATA int is_init;
	DATA int debug_id;
	DATA int max_debug_frames;
	DATA int debug_frame;
	DATA btl_chr_struct* debug_btl_chr;
	extern u8 battle_pause;
	extern u16 DEBUG_MODE;
	extern u16 VERBOSE_MODE;
	extern u16 btl_auto_cooking;
	extern u8 btl_item_count;
	extern int btl_cooking_flag;
	extern u8 btl_unka790;
	extern u8 btl_unk8151;
	extern u16 btl_unk813e;
	extern u16 encount_group_no;
	extern bool checkBtlFinality();
	DATA Voice_Queue voice_queue[NUM_VOICE_QUEUES];
	DATA Text_Container text_container[NUM_TEXT_CONTAINERS];
	DATA Skit_Container skit_container;

	////////////////////////
	// HELPER FUNCTIONS
	////////////////////////

	// centering text to center of the screen :)
	void center_text(fontenv_struct* font, const char* str)
	{
		get_str_width(font, str, 0, 0);
		font->x = GS_X_COORD(SCREEN_WIDTH / 2) - (font->width / 2);
	}
	
	int monster_book_compare(int id1, int id2)
	{
		char* name1 = getMonsterName(id1);
		char* name2 = getMonsterName(id2);
		if (id1 < 7)
		{
			name1 = getEncodedCharName(0xb, id1);
		}
		if (id2 < 7)
		{
			name2 = getEncodedCharName(0xb, id2);
		}
		return strcmp(name1, name2);
	}

	// title screen
	void write_title_strings(fontenv_struct* fnt, const char* original_string)
	{
		u16 width;
		// first draw the existing string we replaced
		// can edit fontenv fntenv here before the draw if needed
		draw_string(fnt, original_string);

		// X coord is right-aligned to screen_width-12, mimicking Inomata's text
		get_str_width(fnt, TITLE_LINE_1, &width, 0);
		fnt->x = GS_X_COORD(628) - width;
		fnt->y = GS_Y_COORD(388);
		draw_string(fnt, TITLE_LINE_1);

		// X coord is right-aligned to screen_width-12, mimicking Namco's text
		get_str_width(fnt, TITLE_LINE_2, &width, 0);
		fnt->x = GS_X_COORD(628) - width;
		fnt->y = GS_Y_COORD(411);
		draw_string(fnt, TITLE_LINE_2);
	}

	////////////////////////
	// SKIT CENTERING CODE
	////////////////////////

	// when skit triggered, process text and set amount of lines
	void process_skit_line(char* str)
	{
		// initialize skit container
		skit_container.num_lines = 1;
		skit_container.string = str;

		// shitty loop thru text until we find 01
		while (true)
		{
			u8 chr = str[0];
			// check for command chars 4 thru f
			if (chr >= 0x4 && chr <= 0xf)
			{
				// if find one, ignore next 4 bytes
				str += 5;
			}
			else
			{
				if (chr == 0x01)
				{
					// newline!
					skit_container.num_lines = 2;
					return;
				}
				else if (chr == 0x0)
				{
					// null byte, end of string, only one line
					return;
				}
				else
				{
					str++;
				}
			}
		}
	}

	// func_00105430
	char* fontenv_process_lines(fontenv_struct* font, fontenv_unk1* font_meta, char* text)
	{
		fontenv_struct font_copy;
		s32 is_page_break;

		// copy the fontenv just in case the width calculation
		// is destructive, game often makes copies so I guess it is
		font_copy = *font;
		// The copy won't be drawn, so we add the NO_DRAW flag so
		// we only get the width calculations without setting up
		// any unintended global data
		font_copy.font_type |= 0x20; 
		
		font->unk_38 = 0;
		font->unk_34 = 0;
		font->unk_06 = font->y;
		font->unk_2a = 0;
		is_page_break = 0;
		while(*text != 0 && is_page_break == 0) {
			// Calculate widths for the text using the copy
			func_00105568(&font_copy, font_meta, text);
			
			// Center da line
			font->x = GS_X_COORD(SCREEN_WIDTH / 2) - (font_copy.unk_2c / 2);

			// Now that it's centered we let the game go on its way
			// font_meta will keep track of the relevant tags for us
			// quite convenient I must say
			text = func_00105568(font, font_meta, text);

			if (font->unk_34 < font->unk_2c) {
				font->unk_34 = font->unk_2c;
			}

			font->unk_38 += font->unk_30;
			if (font->unk_2c != 0) {
				font->unk_2a++;
			}

			switch (*text) {
			case 1:
				// ignore new line char
				text += 1;
				break;
			case 2:
				// End of paragraph
				is_page_break = 1;
				break;
			}
			text = func_001052F0(font, font_meta, text);
		}
		return text;
	}

    // func_00105380
	char* fontenv_process_paragraph(fontenv_struct* font, fontenv_unk1* font_meta, char* text)
	{
		font->width = 0;
		font->height = 0;
		while(*text != 0) {
			text = fontenv_process_lines(font, font_meta, text);
			
			if (font->width < font->unk_34) {
				font->width = font->unk_34;
			}
			
			if (font->height < font->unk_38) {
				font->height = font->unk_38;
			}
			
			if (*text == 2) {
				text = text + 1;
			}
			text = func_001052F0(font, font_meta, text);
		}
		return text;
	}
	
	// processed each frame, replace original draw_string with our multi-draw string
	// also centering both strings, replacing the game's original center
	void draw_skit(fontenv_struct* font)
	{
		// set y for vertically centered
		if (skit_container.num_lines == 1)
		{
			font->y = GS_Y_COORD(408);
		}
		else
		{
			font->y = GS_Y_COORD(396);
		}
		fontenv_draw_centered(font, skit_container.string);
	}

	void fontenv_draw_centered(fontenv_struct* font, char* text)
	{
		fontenv_struct font_copy = *font;
		fontenv_unk1 fnt1 = {};
		fontenv_unk2 fnt2 = {};
		func_00105030(&font_copy, &fnt1, &fnt2, text);
		fontenv_process_paragraph(&font_copy, &fnt1, text);
		fontenv_render(&font_copy, &fnt1);
		// text = func_001052F0(&font_copy, 0x0, text);
	}

	////////////////////////
	// BATTLE SUB CODE
	////////////////////////

	// initialize fontenv and text container ids
	void init_subs()
	{
		if (!is_init)
		{
			fontenv.scale_x = TO_FP16(24);
			fontenv.scale_y = TO_FP16(11);
			fontenv.scale_x2 = TO_FP16(16);
			fontenv.scale_y2 = TO_FP16(16);
			fontenv.color = 0x80808080;
			fontenv.unk_18 = 0x7fffff0;
			is_init = 1;
			for (int i = 0; i < NUM_TEXT_CONTAINERS; i++)
			{
				text_container[i].Container_Id = i;
			}
		}
	}

	// create debug text and draw it
	void draw_debug()
	{
		// check for debug mode
		if (DEBUG_MODE)
		{
			if (debug_id != 0)
			{
				// if we have a btl_chr_struct, use getbtlvocietimer to get timing
				if (debug_btl_chr != 0)
				{
					max_debug_frames = getBtlVoiceTimer(debug_btl_chr, debug_id);
				}
				// or just set it to 999 not like it matters a ton
				else
				{
					max_debug_frames = 999;
				}
				// sprintf format debug string
				char debug[] = "ID: 0x%08X" "\x01" "Frame: %d/%d";
				char debug_str[50];
				if (!battle_pause)
				{
					// incr frame counter if not paused
					debug_frame++;
				}
				if (debug_frame > max_debug_frames)
				{
					// cap frame to max frame
					debug_frame = max_debug_frames;
				}
				// sprintf - write formatted string to debug_str so we can draw it
				sprintf(debug_str, debug, debug_id, debug_frame, max_debug_frames);
				// set x and y
				fontenv.x = DEBUG_X;
				fontenv.y = DEBUG_Y;
				// draw debug_str
				draw_string(&fontenv, debug_str);
			}
		}
	}

	// add battle sub item to voice queue
	void add_to_queue(btl_chr_struct* btl_chr, const Battle_Subs_Table* table)
	{
		// first check if this table is already in our queue
		for (int i = 0; i < NUM_VOICE_QUEUES; i++)
		{
			if (voice_queue[i].table == table)
			{
				// if so, exit and do nothing
				return;
			}
		}
		// next, look for first available queue slot
		for (int i = 0; i < NUM_VOICE_QUEUES; i++)
		{
			if (voice_queue[i].table == 0)		// -- maybe change this to check queue state?
			{
				// and initialize there
				//voice_queue[i].Trigger_Type = type;
				voice_queue[i].btl_chr = btl_chr;
				voice_queue[i].table = table;
				voice_queue[i].current_frame = 0;
				if (btl_chr == 0)
				{
					// if no btl_chr, got here from playAbsVoice, so just set it to playing
					voice_queue[i].queue_state = QUEUE_PLAYING;
				}
				else
				{
					voice_queue[i].queue_state = QUEUE_QUEUED;
				}
				return;
			}
		}
		return;
	}

	// clear voice queue item helper
	void clear_queue_item(Voice_Queue* queue)
	{
		queue->btl_chr = 0;
		queue->table = 0;
		queue->queue_state = QUEUE_OFF;
		queue->current_frame = 0;
	}

	// clear text container item helper
	void clear_container_item(Text_Container* txt)
	{
		txt->container_state = CONTAINER_OFF;
		txt->btl_chr = 0;
		txt->Battle_Voice_Id = 0;
		txt->Line = 0;
		txt->Current_Post_Frame = 0;
		txt->Extra_Frames = 0;
		txt->Current_Frame = 0;
		txt->Total_Lines = 0;
	}

	// initialize text container with voice data
	Text_Container* init_container(btl_chr_struct* btl_chr, const Voice_Line* line, u32 voice_id, int num_lines, int start_frame)
	{
		// loop through containers
		for (int i = 0; i < NUM_TEXT_CONTAINERS; i++)
		{
			// find an empty one
			if (text_container[i].container_state == CONTAINER_OFF)
			{
				// initialize it
				text_container[i].container_state = CONTAINER_ON;
				text_container[i].btl_chr = btl_chr;
				text_container[i].Line = line;
				text_container[i].Battle_Voice_Id = voice_id;
				text_container[i].Current_Frame = start_frame;
				text_container[i].x = DEBUG_X;
				// change y depending on line type
				int y = LINE_Y_BEHIND_UI;
				if (text_container[i].Line->Type == TYPE_BOTTOM || text_container[i].Line->Type == TYPE_NORMAL)
				{
					// check for character UI display to change the y to above UI if its displayed
					if (checkBtlFinality() == 0 && btl_unka790 != 5 && btl_unk813e == 0 && 
						btl_unk8151 == 0 && encount_group_no != 0x31)
					{
						y = LINE_Y_ABOVE_UI;
					}
				}
				else if (text_container[i].Line->Type == TYPE_POST_BATTLE)
				{
					y = LINE_Y_POSTBATTLE_BASE;
					if ((btl_cooking_flag != -1) && ((btl_auto_cooking & 2) == 0))
					{
						y = GS_Y_COORD(268);
					}
					if (btl_item_count > 0)
					{
						int rows = ((btl_item_count + 1) / 2) - 1;
						int coord = 256 - (28 * rows);
						y = GS_Y_COORD(coord);
					}
					if (num_lines == 1 && text_container[i].Container_Id == 0)
					{
						y += Y_COORD(11);
					}
				}
				// should be c0? b0? adjust if needed
				// increases y for second line
				text_container[i].y = y + (Y_COORD(11) * text_container[i].Container_Id); // chg if needed
				return &text_container[i];
			}
		}
		return 0;
	}

	// check voice queue for activity
	// if something needs to be added to queue (start frame trigger)
	void check_queues()
	{
		// loop through all items in the queue
		for (int i = 0; i < NUM_VOICE_QUEUES; i++)
		{
			// if state is queued:
			if (voice_queue[i].queue_state == QUEUE_QUEUED)
			{
				// check if playing
				// what if btl_chr is null..?
				if (voice_queue[i].btl_chr == 0)
				{
					// just set it to playing - this should never reach here
					// but added a check just in case
					voice_queue[i].queue_state = QUEUE_PLAYING;
				}
				else if (voice_queue[i].btl_chr->playing_voice_id == voice_queue[i].table->voice_id)
				{
					// playing, set state
					voice_queue[i].queue_state = QUEUE_PLAYING;
				}
				// check if still queued
				else if (voice_queue[i].btl_chr->queued_voice_id != voice_queue[i].table->voice_id)
				{
					// no longer queued, lets cancel it
					clear_queue_item(&voice_queue[i]);
				}
			}
			// if state is playing:
			if (voice_queue[i].queue_state == QUEUE_PLAYING)
			{
				// check btl_chr not null first so we dont break shit
				// then check if sound is still playing
				if (voice_queue[i].btl_chr != 0 && voice_queue[i].btl_chr->playing_voice_id != voice_queue[i].table->voice_id)
				{
					// done playing, so we need to clear out the queue
					clear_queue_item(&voice_queue[i]);
				}
				else
				{
					// loop through all lines
					for (int j = 0; j < voice_queue[i].table->num_lines; j++)
					{
						// check if current frame == line start frame
						if (voice_queue[i].table->Lines[j]->Start_Frame == voice_queue[i].current_frame)
						{
							// if so, initialize a text container with that line
							init_container(voice_queue[i].btl_chr, voice_queue[i].table->Lines[j], voice_queue[i].table->voice_id, voice_queue[i].table->num_lines, voice_queue[i].current_frame);
						}
					}
					if (!battle_pause)
					{
						// increment frame counter if not paused
						voice_queue[i].current_frame += 1;
					}
				}
			}
		}
	}

	// check text containers for activity
	// if sound done playing, 
	void check_containers()
	{
		// loop through all containers
		// need to check if done so can start the fade out process
		for (int i = 0; i < NUM_TEXT_CONTAINERS; i++)
		{
			Text_Container* txt = &text_container[i];
			if (txt->container_state == CONTAINER_ON)
			{
				if (txt->btl_chr != 0)
				{
					if (txt->btl_chr->playing_voice_id != txt->Battle_Voice_Id)
					{
						// done - start post-process
						txt->container_state = CONTAINER_POST;
					}
				}
				// check if current frame > frame end
				if (txt->Current_Frame >= txt->Line->End_Frame)
				{
					// done - start post-process
					txt->container_state = CONTAINER_POST;
				}
				if (!battle_pause)
				{
					// incr frame counter if not paused
					txt->Current_Frame += 1;
				}
			}
			// if we're in post process mode
			if (txt->container_state == CONTAINER_POST)
			{
				// check if post frame reaches limit
				if (txt->Current_Post_Frame >= POST_FRAME_COUNT)
				{
					// done, clear the item
					clear_container_item(txt);
				}
				else
				{
					// if not done and if not paused
					if (!battle_pause)
					{
						// increment post frame counter
						txt->Current_Post_Frame += 1;
					}
				}
			}
		}
	}

	// clear out voice queue and text containers
	// used when battle ended
	void clear_subs()
	{
		for (int i = 0; i < NUM_VOICE_QUEUES; i++)
		{
			clear_queue_item(&voice_queue[i]);
		}
		for (int i = 0; i < NUM_TEXT_CONTAINERS; i++)
		{
			clear_container_item(&text_container[i]);
		}
		if (DEBUG_MODE)
		{
			// also reset debug data
			debug_id = 0;
			debug_btl_chr = 0;
			debug_frame = 0;
		}
	}

	// main loop for drawing subs
	void draw_subs()
	{
		init_subs();			// initialize subs
		draw_debug();			// draw debug
		check_queues();			// check queue for items to add to containers, or to remove from queue
		check_containers();		// check container for items that are done, handle frame counting
	
		// loop through text containers
		for (int i = 0; i < NUM_TEXT_CONTAINERS; i++)
		{
			Text_Container* txt = &text_container[i];
			// if state is anything larger than off (on or post process), draw
			if (txt->container_state > CONTAINER_OFF)
			{
				// set fontenv data
				const char* str = txt->Line->String;
				fontenv.x = txt->x;
				fontenv.y = txt->y;
				// get percentage remaining to adjust opacity
				int remaining_frames = POST_FRAME_COUNT - txt->Current_Post_Frame;
				// alpha/opacity adjustment for fade
				u32 alpha = ((remaining_frames * 0x80) / POST_FRAME_COUNT);
				fontenv.color = 0x00808080 + (alpha << 24);
				// center and draw
				center_text(&fontenv, str);
				draw_string(&fontenv, str);
			}
		}
	}

	// triggers on voice trigger, process sound if in our table
	void setup_text(btl_chr_struct* btl_chr, int _voice_id)
	{
		// get voice id, extract char id (two high bytes)
		int voice_id = _voice_id;
		int char_id = (voice_id & 0xFF000000) >> 24;	// guess the & isnt needed since we're shifting... whatever
		
		// if we have btl_chr, and if the char id isn't 8
		// there's weirdness where sometimes the char id isnt embedded in the voice id
		// for example, we might have veigue play 0x01000022, but this passes in 0x00000022
		// we still want the 0x01 on the high bytes so we can grab the right data
		if (btl_chr != 0 && char_id != 8) // char_id != 0?
		{
			// or the id with the char id from btl_chr
			voice_id = voice_id | (btl_chr->char_id << 24);
		}
		// binary search for the voice
		const Battle_Subs_Table* table =
			bsearch<const Battle_Subs_Table, u32>(battle_subs_tables, Battle_Table_Count, voice_id);
		if (table != 0)
		{
			// found, add to voice queue
			add_to_queue(btl_chr, table);
		}
		// if debug mode
		if (DEBUG_MODE)
		{
			// if we're in verbose mode, always add, otherwise only add if char id is > 6 (not a basic character sound)
			// disable verbose mode to hunt for mystic artes, story dialog in battles, etc.
			if (VERBOSE_MODE || char_id > 6)
			{
				debug_frame = 0;
				debug_id = voice_id;
				max_debug_frames = -1;
				debug_btl_chr = btl_chr;
			}
		}
	}
};