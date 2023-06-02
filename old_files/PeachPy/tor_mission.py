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

pointer_start = 0x1870
pointer_end = 0x1C40

text_start = 0x3961
text_end = 0x3ED8

def mkdir(name):
    try: os.mkdir(name)
    except: pass

#############################################
#                                           #
#             Extract Function              #
#                                           #
#############################################

def extract_missions():
    print("Extracting Mission Strings...")
    mkdir('Mission_txt/')
    print("Directory Made")

    json_file = open('tor_tbl.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    name = "00023_0000d"
    f = open("00023/00023_0000d.unknown", 'rb')

    miss_file = open('miss.json', 'w')
    miss_data = {}

    text_pointers = []
    addrs = []

    f.seek(pointer_start)

    while f.tell() < pointer_end:
        addr = struct.unpack('<L', f.read(4))[0]
        if text_start <= addr <= text_end:
            addrs.append(f.tell() - 4)
            text_pointers.append(addr)
        else:
            continue

    o = open("Mission_txt/" + name + ".txt", "w", encoding="utf-8")

    miss_data[name] = []

    for i in range(len(text_pointers)):
        f.seek(text_pointers[i] - 1, 0)
        b = f.read(1)
        if b != b"\x00":
            continue
        miss_data[name].append(addrs[i])
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



    json.dump(miss_data, miss_file, indent=4)

#############################################
#                                           #
#             Reinsert Function             #
#                                           #
#############################################

def insert_missions():
    print("Reinserting Mission Strings...")
    json_file = open("TOR_TBL.json", "r")
    miss_json = open("miss.json", "r")
    table = json.load(json_file)
    miss_data = json.load(miss_json)
    json_file.close()
    miss_json.close()

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

    mkdir("mission_new/")

    for name in os.listdir("mission_txt/"):
        f = open("mission_txt/" + name, "r", encoding="utf8")
        name = name[:-4]
        e = open("00023/00023_0000d.unknown", "rb")
        o = open("mission_new/" + name + '.unknown', "wb")

        txts = []
        sizes = []
        txt = bytearray()

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

        if sum(sizes) >= 0x577:
            print("Error: Length of Text Block is Too Long. \n Text Block must be no larger than 1406 bytes \n in length unless you want your precious \n strings to get overwritten!")
            continue
        e.seek(0, 0)
        header = e.read(text_start)
        o.write(header + b"\x00")
        e.close()

        pos = 0x3961
        for i in range(len(txts)):
            o.seek(miss_data[name][i], 0)
            o.write(struct.pack("<L", pos))
            pos += sizes[i]

        o.seek(text_start, 0)

        for t in txts:
            o.write(t)
        o.close()


if __name__ == '__main__':
    if sys.argv[1] == 'help':
        print("Tales of Rebirth Panic Dreamer Mission Strings Extraction/Reinsertion tool. \n By SymphoniaLauren.\n Usage: \n py tor_mission.py extract missions -- extracts mission strings. \n py tor_mission.py insert missions -- inserts missions strings.")
    if sys.argv[1] == 'extract' and sys.argv[2] == 'missions':
        extract_missions()
    if sys.argv[1] == 'insert' and sys.argv[2] == 'missions':
        insert_missions()
    else:
        sys.exit(1)