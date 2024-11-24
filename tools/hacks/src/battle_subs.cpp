#include "Externs.h"
#include "Sub_Types.h"
#include "battle_subs_text.h"
#include "battle_subs.h"

#define DEBUG_X 0x6d00				// debug x
#define DEBUG_Y 0x8300//0x7920				// debug y
#define LINE_1_Y 0x8300				// y for type 1
#define LINE_2_Y 0x8580				// y for type 2
#define LINE_3_Y 0x8300				// y for type 3
#define NUM_VOICE_QUEUES 6			// slots to hold active/pending voice data, 6 is fine
#define NUM_TEXT_CONTAINERS 2		// number of active sub lines - may need to adj code if increasing
#define POST_FRAME_COUNT 20			// number of frames for fade out animation

extern "C"
{
	fontenv_struct fontenv __attribute__((section(".data")));
	int is_init __attribute__((section(".data")));
	int debug_id __attribute__((section(".data")));
	int max_debug_frames __attribute__((section(".data")));
	int debug_frame __attribute__((section(".data")));
	btl_chr_struct* debug_btl_chr __attribute__((section(".data")));
	extern u8 battle_pause;
	extern u16 DEBUG_MODE;
	extern u16 VERBOSE_MODE;
	Voice_Queue voice_queue[NUM_VOICE_QUEUES] __attribute__((section(".data")));
	Text_Container text_container[NUM_TEXT_CONTAINERS] __attribute__((section(".data")));
	Skit_Container skit_container __attribute__((section(".data")));

	////////////////////////
	// HELPER FUNCTIONS
	////////////////////////

	// centering text to center of the screen :)
	void center_text(fontenv_struct* font, const char* str)
	{
		get_str_width(font, str, 0, 0);
		font->x = 0x8000 - (font->width / 2);
	}

	////////////////////////
	// SKIT CENTERING CODE
	////////////////////////

	// clear skit container, run when skit ends
	void clear_skit()
	{
		skit_container.num_lines = 0;
		skit_container.string_1 = 0;
		skit_container.string_2 = 0;
	}

	// when skit triggered, process text and split string into two
	void process_skit_line(char* str)
	{
		// first, if there is a previous 2nd string, repair the \0 with a \n
		if (skit_container.string_2 != 0)
		{
			skit_container.string_2[-1] = 1;	// replace previous index with new line
		}

		// initialize skit container
		skit_container.num_lines = 1;
		skit_container.string_1 = str;
		skit_container.string_2 = 0;

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
					str[0] = 0; // set it to 0
					str += 1;
					// and adjust skit container for 2nd string
					skit_container.string_2 = str;
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
	
	// processed each frame, replace original draw_string with our multi-draw string
	// also centering both strings, replacing the game's original center
	void draw_skit(fontenv_struct* font)
	{
		// if only one line
		if (skit_container.num_lines == 1)
		{
			// set y for centered
			font->y = 0x85C0;
			// center and draw line
			center_text(font, skit_container.string_1);
			draw_string(font, skit_container.string_1);
		}
		else
		{
			// set y for two liness
			font->y = 0x8560;
			// center and draw line 1
			center_text(font, skit_container.string_1);
			draw_string(font, skit_container.string_1);
			// increase y
			// center and draw line 2
			font->y = 0x8560 + 0xc0;
			center_text(font, skit_container.string_2);
			draw_string(font, skit_container.string_2);
		}
	}

	////////////////////////
	// BATTLE SUB CODE
	////////////////////////

	// initialize fontenv and text container ids
	void init_subs()
	{
		if (!is_init)
		{
			fontenv.scale_x = 0x180;
			fontenv.scale_y = 0xb0;
			fontenv.scale_x2 = 0x100;
			fontenv.scale_y2 = 0x100;
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
	void add_to_queue(btl_chr_struct* btl_chr, Battle_Subs_Table* table)
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
	Text_Container* init_container(btl_chr_struct* btl_chr, Voice_Line* line, u32 voice_id)
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
				text_container[i].x = DEBUG_X;
				// change y depending on line type
				int y = LINE_1_Y;
				if (text_container[i].Line->Type == TYPE_BOTTOM)
				{
					y = LINE_2_Y;
				}
				else if (text_container[i].Line->Type == TYPE_POST_BATTLE)
				{
					y = LINE_3_Y;
				}
				// should be c0? b0? adjust if needed
				// increases y for second line
				text_container[i].y = y + (0xB8 * text_container[i].Container_Id); // chg if needed
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
							init_container(voice_queue[i].btl_chr, voice_queue[i].table->Lines[j], voice_queue[i].table->voice_id);
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
		Battle_Subs_Table* table =
			bsearch<Battle_Subs_Table, u32>(battle_subs_tables, Battle_Table_Count, voice_id);
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