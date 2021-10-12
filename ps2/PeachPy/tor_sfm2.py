import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string

#constants
TAGS = {
    0x5: "color",
    0xB: "name",
    0xF: "voice",
    0x6: "size",
    0xC: "item",
    0xD: "button",
}

names = {
    1: "Veigue",
    2: "Mao",
    3: "Eugene",
    4: "Annie",
    5: "Tytree",
    6: "Hilda",
    7: "Claire_Agarte",
    8: "Agarte_Claire",
    9: "Annie (NPC)",
    0x1FFF: "OnScreenChar",
}

colors = {
    1: "Blue",
    2: "Red",
    3: "Purple",
    4: "Green",
    5: "Cyan",
    6: "Yellow",
    7: "White",
}

PRINTABLE_CHARS = "".join(
    (string.digits, string.ascii_letters, string.punctuation, " ")
)

COMMON_TAG = r"(<\w+:?\w+>)"
HEX_TAG = r"(\{[0-9A-F]{2}\})"

def mkdir(name):
    try: os.mkdir(name)
    except: pass

#############################################
#                                           #
#             Extract Function              #
#                                           #
#############################################

def extract_sfm2():
    print("Extracting SFM2")
    mkdir('TXT/')
    print("Directory Made")
    #json_file = open('TBL.json', 'w')
    #json_data = {}
    #char_file = open('00015.bin', 'r', encoding='cp932')
    #char_index = char_file.read()
    #char_file.close()

    json_file = open('tor_tbl.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    sfm2_file = open('sfm2.json', 'w')
    sfm2_data = {}
    sfm2_pointers = open('sfm2_point.json', 'w')
    sfm2_p_data = {}
    
    for name in os.listdir('sfm2/'):
        f = open('sfm2/' + name, 'rb')
        header = f.read(4)
        if header != b'SFM2':
            continue
        sfm2_data[name] = []
        f.seek(0xC)
        code_block_size = struct.unpack('<L', f.read(4))[0]
        text_block_size = struct.unpack('<L', f.read(4))[0]
        table_size = struct.unpack('<L', f.read(4))[0]
        f.seek(0x18)
        pointer_block = struct.unpack('<L', f.read(4))[0]
        text_block = struct.unpack('<L', f.read(4))[0]
        table_block = struct.unpack('<L', f.read(4))[0]
        if text_block == 0:
            continue
        print("Extracting " + name)
        fsize = os.path.getsize('sfm2/' + name)
        text_pointers = []
        addrs = []
        pointer_type = []
        sfm2_p_data[name] = []
        if table_block == 0x600:
            print("Hewwo owo")
            f.seek(table_block, 0)
            while f.tell() < text_block:
                b = struct.unpack('<L', f.read(4))[0]
                if b & (b - 1) == 0:
                    off = struct.unpack('<L', f.read(4))[0]
                    addrs.append(f.tell() - 4)
                    addr = (-(text_block - table_block - off))
                    text_pointers.append(addr)
                    pointer_type.append("Table")
                else:
                    continue

        f.seek(pointer_block, 0)
        
        while f.tell() < table_block:
            b = f.read(1)
            if b == b'\x37':
                if f.read(1) == b'\02':
                    addr = struct.unpack('B', f.read(1))[0]
                    if (addr < text_block_size):
                        addrs.append(f.tell() - 1)
                        text_pointers.append(addr)
                        pointer_type.append("1")

                else:
                    continue
            elif b == b'\x47':
                if f.read(1) == b'\02':
                    addr = struct.unpack('<H', f.read(2))[0]
                    if (addr < text_block_size) and (addr > 0):
                        addrs.append(f.tell() - 2)
                        text_pointers.append(addr)
                        pointer_type.append("2")
                else:
                    continue
        



        if len(text_pointers) == 0:
            continue
        o = open("txt/" + name + ".txt", "w", encoding="utf-8")
        for i in range(len(text_pointers)):
            f.seek(text_block + text_pointers[i] - 1, 0)
            b = f.read(1)
            if b != b"\x00":
                continue
            sfm2_data[name].append(addrs[i])
            sfm2_p_data[name].append(pointer_type[i])
            b = f.read(1)
            while b != b"\x00":
                b = ord(b)
                if (b >= 0x99 and b <= 0x9F) or (b >= 0xE0 and b <= 0xEB):
                    c = (b << 8) + ord(f.read(1))
                    # if str(c) not in json_data.keys():
                    #    json_data[str(c)] = char_index[decode(c)]
                    o.write(json_data[str(c)])
                elif b == 0x1:
                    o.write("\n")
                elif b in (0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xB, 0xC, 0xD, 0xE, 0xF):
                    b2 = struct.unpack("<L", f.read(4))[0]
                    if b in TAGS:
                        tag_name = TAGS.get(b)
                        tag_param = None
                        if (tag_name + "s") in globals():
                            tag_param = eval("%ss.get(b2, None)" % tag_name)
                        if tag_param != None:
                            o.write("<%s>" % tag_param)
                        else:
                            o.write("<%s:%08X>" % (tag_name, b2))
                    else:
                        o.write("<%02X:%08X>" % (b, b2))
                elif chr(b) in PRINTABLE_CHARS:
                    o.write(chr(b))
                elif b >= 0xA1 and b < 0xE0:
                    o.write(struct.pack("B", b).decode("cp932"))
                elif b in (0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19):
                    o.write("{%02X}" % b)
                    next_b = b""
                    while next_b != b"\x80":
                        next_b = f.read(1)
                        o.write("{%02X}" % ord(next_b))
                elif b == 0x81:
                    next_b = f.read(1)
                    if next_b == b"\x40":
                        o.write("　")
                    else:
                        o.write("{%02X}" % b)
                        o.write("{%02X}" % ord(next_b))
                else:
                    o.write("{%02X}" % b)
                b = f.read(1)
            o.write("\n[ENDBLOCK]\n")
        f.close()
        o.close()



    json.dump(sfm2_data, sfm2_file, indent=4)
    json.dump(sfm2_p_data, sfm2_pointers, indent=4)

#############################################
#                                           #
#             Reinsert Function             #
#                                           #
#############################################

def insert_sfm2():
    json_file = open("TOR_TBL.json", "r")
    sfm2_json = open("SFM2.json", "r")
    pointer_json = open("sfm2_point.json", "r")
    table = json.load(json_file)
    sfm2_data = json.load(sfm2_json)
    pointer_data = json.load(pointer_json)
    json_file.close()
    sfm2_json.close()

    itable = dict([[i, struct.pack(">H", int(j))] for j, i in table.items()])
    itags = dict([[i, j] for j, i in TAGS.items()])
    inames = dict([[i, j] for j, i in names.items()])
    icolors = dict([[i, j] for j, i in colors.items()])
    unames = []
    for i in names.values():
        nam = "<" + str(i) + ">"
        unames.append(nam)
    ucolors = []
    for i in colors.values():
        col = "<" + str(i) + ">"
        ucolors.append(col)

    mkdir("sfm2_NEW/")

    for name in os.listdir("txt_en"):
        f = open("txt_en/" + name, "r", encoding="utf8")
        name = name[:-4]
        sfm2 = open("sfm2/" + name, "rb")
        o = open("sfm2_new/" + name, "wb")

        txts = []
        sizes = []
        txt = bytearray()

        #this is the text conversion to bytes#
        for line in f:
            line = line.strip("\x0A")
            if len(line) > 0:
                if line[0] == "#":
                    continue
            if line == "[ENDBLOCK]":
                if len(line) == 0:
                    txts.append(b"\x00")
                else:
                    txts.append(txt[:-1] + b"\x00")
                sizes.append(len(txt))
                txt = bytearray()
            else:
                string_hex = re.split(HEX_TAG, line)
                string_hex = [sh for sh in string_hex if sh]
                for s in string_hex:
                    if re.match(HEX_TAG, s):
                        txt += struct.pack("B", int(s[1:3], 16))
                    else:
                        s_com = re.split(COMMON_TAG, s)
                        s_com = [sc for sc in s_com if sc]
                        for c in s_com:
                            if re.match(COMMON_TAG, c):
                                if ":" in c:
                                    split = c.split(":")
                                    if split[0][1:] in itags.keys():
                                        txt += struct.pack("B", itags[split[0][1:]])
                                        txt += struct.pack("<I", int(split[1][:8], 16))
                                    else:
                                        txt += struct.pack("B", int(split[0][1:], 16))
                                        txt += struct.pack("<I", int(split[1][:8], 16))
                                if c in unames:
                                    txt += struct.pack("B", 0xB)
                                    txt += struct.pack("<I", inames[c[1:-1]])
                                if c in ucolors:
                                    txt += struct.pack("B", 0x5)
                                    txt += struct.pack("<I", icolors[c[1:-1]])
                            else:
                                for c2 in c:
                                    if c2 in itable.keys():
                                        txt += itable[c2]
                                    else:
                                        txt += c2.encode("cp932")
                txt += b"\x01"

        f.close()

        sfm2.seek(0xC, 0)
        code_block_size = struct.unpack('<L', sfm2.read(4))[0]
        text_block_size = struct.unpack('<L', sfm2.read(4))[0]
        table_size = struct.unpack('<L', sfm2.read(4))[0]
        pointer_block = struct.unpack("<L", sfm2.read(4))[0]

        sfm2.seek(0x18)
        pointer_block = struct.unpack('<L', sfm2.read(4))[0]
        text_block = struct.unpack('<L', sfm2.read(4))[0]
        table_block = struct.unpack('<L', sfm2.read(4))[0]

        sfm2.seek(0, 0)
        teh_file = sfm2.read(text_block)
        o.write(teh_file)

        pos = 0

        for i in range(len(txts)):
            o.seek(sfm2_data[name][i], 0)
            if pointer_data[name][i] == 'Table':
                o.write(struct.pack("<H", pos + 0x54))
                pos += sizes[i]
            elif pointer_data[name][i] == '1':
                o.write(struct.pack("B", pos))
                pos += sizes[i]
            elif pointer_data[name][i] == '2':
                o.write(struct.pack("<H", pos))
                pos += sizes[i]

        o.seek(text_block, 0)

        for t in txts:
            o.write(t)

        New_Text_Size = sum(sizes)

        o.seek(8, 0)
        o.write(struct.pack("<L", New_Text_Size + text_block))
        o.seek(0x10, 0)
        o.write(struct.pack("<L", New_Text_Size))
        sfm2.close
        o.close

if __name__ == '__main__':
    if sys.argv[1] == 'help':
        print("Tales of Rebirth SFM2 Extraction/Reinsertion tool. \n By SymphoniaLauren.\n Usage: \n py tor_sfm2.py extract sfm2 -- extracts strings from SFM2 files. \n py tor_sfm2.py insert sfm2 -- inserts strings from SFM2 files.")
    if sys.argv[1] == 'extract' and sys.argv[2] == 'sfm2':
        extract_sfm2()
    if sys.argv[1] == 'insert' and sys.argv[2] == 'sfm2':
        insert_sfm2()
    else:
        sys.exit(1)