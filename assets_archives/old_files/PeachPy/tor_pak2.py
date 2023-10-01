import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string

tags = {0x5: 'color', 0xB: 'name', 0xF: 'voice', 0x06: 'size', 0xC: 'item', 0xD: 'button'}
names = {1: 'Veigue', 2: 'Mao', 3: 'Eugene', 4: 'Annie', 5: 'Tytree', 6: 'Hilda',
         7: 'Claire/Agarte', 8:'Agarte/Claire', 9:'Annie (NPC)', 0x1FFF: 'OnScreenChar'}
colors = {1: 'Blue', 2: 'Red', 3: 'Purple', 4: 'Green', 5: 'Cyan', 6: 'Yellow', 7: 'White'}
printable = ''.join((string.digits,string.ascii_letters,string.punctuation,' '))

def mkdir(name):
    try: os.mkdir(name)
    except: pass

def extract_pak2_theirsce():
    os.mkdir('FILE/pak2/theirsce')
    for file in os.listdir('FILE/pak2/'):
        if not file.endswith('pak2'):
            continue
        f = open('FILE/pak2/' + file, 'rb')
        sexy_file = file.replace('.pak2', '')
        ext = 'theirsce'
        data = f.read()
        theirsce_end = data[4:8]
        end_int = int.from_bytes(theirsce_end, 'little')
        size = end_int - 0x20
        f.seek(0x20, 0)
        filedata = f.read(size)
        o = open('FILE/pak2/theirsce/' + sexy_file + '.' + ext, 'wb')
        o.write(filedata)
        o.close()
    f.close

def extract_theirsce():
    mkdir('FILE/pak2/theirsce/TXT')
    #json_file = open('TBL.json', 'w')
    #json_data = {}
    #char_file = open('00015.bin', 'r', encoding='cp932')
    #char_index = char_file.read()
    #char_file.close()

    json_file = open('tor_tbl.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    theirsce_file = open('THEIRSCE.json', 'w')
    theirsce_data = {}
    
    for name in os.listdir('FILE/pak2/theirsce/'):
        f = open('FILE/pak2/theirsce/' + name, 'rb')
        header = f.read(8)
        if header != b'THEIRSCE':
            continue
        theirsce_data[name] = []
        pointer_block = struct.unpack('<L', f.read(4))[0]
        text_block = struct.unpack('<L', f.read(4))[0]
        fsize = os.path.getsize('FILE/pak2/theirsce/' + name)
        text_pointers = []
        addrs = []
        f.seek(pointer_block, 0)
        
        while f.tell() < text_block:
            b = f.read(1)
            if b == b'\xF8':
                addr = struct.unpack('<H', f.read(2))[0]
                if (addr < fsize - text_block) and (addr > 0):
                    #theirsce_data[name].append(f.tell() - 2)
                    addrs.append(f.tell() - 2)
                    text_pointers.append(addr)
                    
        if len(text_pointers) == 0:
            continue
        
        o = open('FILE/pak2/theirsce/txt/' + name + '.txt', 'w', encoding='utf-8')
        for i in range(len(text_pointers)):
            f.seek(text_block + text_pointers[i] - 1, 0)
            b = f.read(1)
            if b != b'\x00':
                continue
            theirsce_data[name].append(addrs[i])
            b = f.read(1)
            while b != b'\x00':
                b = ord(b)
                if (b >= 0x99 and b <= 0x9F) or (b >= 0xE0 and b <= 0xEB):
                    c = (b << 8) + ord(f.read(1))
                    #if str(c) not in json_data.keys():
                    #    json_data[str(c)] = char_index[decode(c)]
                    o.write(json_data[str(c)])
                elif b == 0x1:
                    o.write('\n')
                elif b in (0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xB, 0xC, 0xD, 0xE, 0xF):
                    b2 = struct.unpack("<L", f.read(4))[0]
                    if b in tags:
                        tag_name = tags.get(b)
                        tag_param = None
                        if (tag_name+'s') in globals():
                            tag_param = eval("%ss.get(b2, None)" % tag_name)
                        if tag_param != None:
                            o.write("<%s>" % tag_param)
                        else:
                            o.write("<%s:%X>" % (tag_name, b2))
                    else:
                        o.write('<%02X:%08X>' % (b, b2))
                elif chr(b) in printable:
                    o.write(chr(b))
                elif b >= 0xA1 and b < 0xE0:
                    o.write(struct.pack('B', b).decode('cp932'))
                elif b in (0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19):
                    o.write('{%02X}' % b)
                    next_b = b''
                    while next_b != b'\x80':
                        next_b = f.read(1)
                        o.write('{%02X}' % ord(next_b))
                elif b == 0x81:
                    next_b = f.read(1)
                    if next_b == b'\x40':
                        o.write('　')
                    else:
                        o.write('{%02X}' % b)
                        o.write('{%02X}' % ord(next_b))
                else:
                    o.write('{%02X}' % b)
                b = f.read(1)
            o.write('\n[ENDBLOCK]\n')
        f.close()
        o.close()

    #json.dump(json_data, json_file, indent=4)
    json.dump(theirsce_data, theirsce_file, indent=4)

if __name__ == '__main__':
    if sys.argv[1] == '1':
        extract_pak2_theirsce
    if sys.argv[1] == '2':
        extract_theirsce()
    else:
        sys.exit(1)