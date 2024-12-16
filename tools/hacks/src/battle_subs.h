#pragma once
extern "C"
{
	// helper functions
	void center_text(fontenv_struct* font, const char* str);
	// skit centering
	void clear_skit();
	void process_skit_line(char* str);
	void draw_skit(fontenv_struct* font);
	// battle subs
	void init_subs();
	void draw_debug();
	void draw_subs();
	void check_containers();
	void check_queues();
	void setup_text(btl_chr_struct* btl_chr, int _voice_id);
	void add_to_queue(btl_chr_struct* btl_chr, const Battle_Subs_Table* table);
	void clear_queue_item(Voice_Queue* queue);
	void clear_container_item(Text_Container* txt);
	Text_Container* init_container(btl_chr_struct* btl_chr, const Voice_Line* line, u32 voice_id, int num_lines, int start_frame);
}