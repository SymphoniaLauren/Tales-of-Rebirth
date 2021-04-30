import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string

tmsk_pointer_begin = 0x410
#tmsk_isize = 0xAC00
tmrc_pointer_begin = 0x450
extension = 'tm2'
#tmsk_num = data[0x404:2]
#tmrc_num = data[0x406:2]
#palette = data[:0x400]
##Header construction info
TIM2_header_magic = b'TIM2\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
TIM2_header_tmskdata = b'\x40\xB0\x00\x00\x00\x04\x00\x00\x00\xAC\x00\x00\x30\x00\x00\x01\x00\x01\x03\x05\x00\x01\xAC\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
TIM2_palette_length = b'\x00\x04\x00\x00'
TIM2_header_length = b'\x30\x00\x00\x01\x00\x01\x03\x05'
blah_blah_blah = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

##and then, pointer_end of tmsk/tmrc pointers is tmsk_num(or tmrc_num)+(n*4)
##each pointer is 4 bytes long
##pointer is relative to the end of the palette data, so the first pointer will read 0x100, but it's actually pointing to 0x500 in the file (0x400+0x100)=0x500
##tmsk all have same data length, image width, image height, could probably just write a single header for those...
##tmrc have variable image length, width, height. Image length isn't indicated in the header, but it is width*height
##final tim2 should be tim header magic + header data + image data + palette 

def mkdir(name):
    try: os.mkdir(name)
    except: pass

def extract_tmsk():
    mkdir('FILE/tmsk/tim2')
    for file in os.listdir('FILE/tmsk/'):
        if not file.endswith('tmsk'):
            continue
        f = open('FILE/tmsk/' + file, 'rb')
        data = f.read()
        palette = data[:0x400]
        tmsk_num = data [0x404:0x406]
        tmsk_num_int = int.from_bytes(tmsk_num, 'little')
        tmsk_pointer_end = tmsk_pointer_begin + (tmsk_num_int * 4)
        sexy_file = file.replace('.tmsk', '')
        f.seek(tmsk_pointer_begin, 0)
        pointers = []
    
        while f.tell() < tmsk_pointer_end:
            p = struct.unpack('<L', f.read(4))[0]
            pointers.append(p)
            
        for i in range(len(pointers)):
            start = pointers[i] + 0x400
            size = 0xAC00
            f.seek(start, 0)
            tmsk_idata = f.read(size)
            o = open('FILE/tmsk/tim2/' + sexy_file +'_' + '%02d.%s' % (i, extension), 'wb')
            o.write(TIM2_header_magic + TIM2_header_tmskdata + tmsk_idata + palette)
            o.close()

    f.close()

def extract_tmrc():
    mkdir('FILE/tmsk/tim2')
    for file in os.listdir('FILE/tmsk/'):
        if not file.endswith('tmsk'):
            continue
        f = open('FILE/tmsk/' + file, 'rb')
        data = f.read()
        palette = data[:0x400]
        tmrc_num = data[0x406:0x408]
        tmrc_num_int = int.from_bytes(tmrc_num, 'little')
        tmrc_pointer_end = tmrc_pointer_begin + (tmrc_num_int * 4)
        sexy_file = file.replace('.tmsk', '')
        
        f.seek(tmrc_pointer_begin, 0)
        pointers = []
    
        while f.tell() < tmrc_pointer_end:
            p = struct.unpack('<L', f.read(4))[0]
            pointers.append(p)

        for i in range(len(pointers)):
            w_start = pointers[i] + 0x400 + 8
            h_start = pointers[i] + 0x400 + 10
            h_end = pointers[i] + 0x400 + 12
            tmrc_w = data[w_start:h_start]
            tmrc_h = data[h_start:h_end]
            tmrc_w_int = int.from_bytes(tmrc_w, 'little')
            tmrc_h_int = int.from_bytes(tmrc_h, 'little')

            i_start = pointers[i] + 0x400 + 128
            isize = tmrc_w_int * tmrc_h_int
            f.seek(i_start)
            tmrc_idata = f.read(isize)
            TIM2_size = isize + 0x40 + 0x400
            TIM2_size_bytes = TIM2_size.to_bytes(4, 'little')
            img_size_bytes = isize.to_bytes(4, 'little')

            o = open('FILE/tmsk/tim2/' + sexy_file +'_' + 'tmrc' + '_' + '%02d.%s' % (i, extension), 'wb')
            o.write(TIM2_header_magic + TIM2_size_bytes + TIM2_palette_length + img_size_bytes + TIM2_header_length + tmrc_w + tmrc_h + blah_blah_blah + tmrc_idata + palette)
            o.close()

    f.close()

if __name__ == '__main__':
    if sys.argv[1] == '1':
        extract_tmsk()
    if sys.argv[1] == '2':
        extract_tmrc()
    else:
        sys.exit(1)