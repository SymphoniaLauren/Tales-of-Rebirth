import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string
import argparse
import textwrap
from pathlib import Path
import comptolib

# Constants
TAGS = {
    0x5: "color",
    0xB: "name",
    0xF: "voice",
    0x6: "size",
    0xC: "item",
    0xD: "button",
}

NAMES = {
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

COLORS = {
    1: "Blue",
    2: "Red",
    3: "Purple",
    4: "Green",
    5: "Cyan",
    6: "Yellow",
    7: "White",
}

SCRIPT_VERSION = "0.1"
POINTERS_BEGIN = 0xD76B0  # Offset to DAT.BIN pointer list start in SLPS_254.50 file
POINTERS_END = 0xE60C8  # Offset to DAT.BIN pointer list end in SLPS_254.50 file
HIGH_BITS = 0xFFFFFFC0
LOW_BITS = 0x3F

COMMON_TAG = r"(<\w+:?\w+>)"
HEX_TAG = r"(\{[0-9A-F]{2}\})"

VALID_FILE_NAME = r"([0-9]{5})(?:\.)?([1,3])?\.(\w+)$"

PRINTABLE_CHARS = "".join(
    (string.digits, string.ascii_letters, string.punctuation, " ")
)


# ============================
#      UTILITY FUNCTIONS
# ============================

def get_file_name(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_dat_folder_file_list(dirName, recurse=True):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath) and recurse:
            allFiles = allFiles + get_dat_folder_file_list(fullPath, False)
        elif re.search(VALID_FILE_NAME, fullPath):
            allFiles.append(fullPath)

    return allFiles


def mkdir(name):
    try:
        os.mkdir(name)
    except:
        pass


def get_directory_path(path):
    return os.path.dirname(os.path.abspath(path))


def get_pointers(elf_path="SLPS_254.50"):

    f = open(os.path.abspath(elf_path), "rb")

    f.seek(POINTERS_BEGIN, 0)
    pointers = []

    while f.tell() < POINTERS_END:
        p = struct.unpack("<L", f.read(4))[0]
        pointers.append(p)

    f.close()
    return pointers


def compress_compto(name, ctype=1):
    c = "-c%d" % ctype
    subprocess.run(["compto", c, name, name + ".c"])


def decompress_compto(name):
    subprocess.run(["compto", "-d", name, name + ".d"])


def decompress_folder(name):
    for f in os.listdir(name):
        if f.endswith("d"):
            continue
        subprocess.run(["compto", "-d", name + f, name + f + ".d"])


def extract_pak1(name):
    subprocess.run(["pakcomposer", "-d", name, "-1", "-u", "-v", "-x"])


def decode(codepoint):
    base_codePoint = 0x9940

    if codepoint < base_codePoint:
        codepoint = base_codePoint

    upper_byte = codepoint >> 8
    lower_byte = codepoint & 0xFF

    if upper_byte >= 0xE0:
        upper_byte = upper_byte - 0x40
    if lower_byte >= 0x80:
        lower_byte = lower_byte - 0x01
    if lower_byte >= 0x5D:
        lower_byte = lower_byte - 0x01

    resulting_character = lower_byte - 0x40
    resulting_character = resulting_character + ((upper_byte - 0x99) * 0xBB)

    return resulting_character


def get_pak_type(data):
    is_aligned = False

    if len(data) < 0x8:
        return None

    files = struct.unpack("<I", data[:4])[0]
    first_entry = struct.unpack("<I", data[4:8])[0]

    # Expectations
    pak1_header_size = 4 + (files * 8)
    pakN_header_size = 4 + (files * 4)

    # Check for alignment
    if first_entry % 0x10 == 0:
        is_aligned = True
        aligned_pak1_size = pak1_header_size + (0x10 - (pak1_header_size % 0x10))
        aligned_pakN_size = pakN_header_size + (0x10 - (pakN_header_size % 0x10))

    # First test pak0 (hope there are no aligned pak0 files...)
    if len(data) > pakN_header_size:
        calculated_size = 0
        for i in range(4, (files + 1) * 4, 4):
            calculated_size += struct.unpack("<I", data[i : i + 4])[0]
        if calculated_size == len(data) - pakN_header_size:
            return "pak0"

    # Test for pak1 & pak3
    if is_aligned:
        if aligned_pak1_size == first_entry:
            return "pak1"
        elif aligned_pakN_size == first_entry:
            return "pak3"
    else:
        if pak1_header_size == first_entry:
            return "pak1"
        elif pakN_header_size == first_entry:
            return "pak3"

    # Test for pak2
    offset = struct.unpack("<I", data[0:4])[0]

    if data[offset:offset+8] == b"THEIRSCE":
        return "pak2"
    elif data[offset:offset+8] == b"IECSsreV":
        return "apak"

    # Didn't match anything
    return None


def move_theirsce():
    mkdir("THEIRSCE")
    theirsce_dir = os.getcwd() + "/theirsce/"

    for folder in os.listdir("scpk"):
        if not os.path.isdir("scpk/" + folder):
            continue
        for sce in os.listdir("scpk/" + folder):
            if sce.endswith(".theirsce"):
                f = sce
                break
        new_name = "%s_%s.theirsce" % (folder, f.split(".")[0])
        shutil.copy(os.path.join("scpk", folder, f), theirsce_dir + new_name)
        print(new_name)


def move_scpk_packed():
    for f in os.listdir("scpk_packed"):
        shutil.copy(os.path.join("scpk_packed", f), "dat/" + f)


def is_compressed(data):
    if struct.unpack("<L", data[1:5])[0] == len(data) - 9:
        return True
    return False


def get_extension(data):
    if data[:4] == b"SCPK":
        return "scpk"

    if data[:4] == b"TIM2":
        return "tm2"

    if data[0xB:0xE] == b"ELF":
        return "irx"

    if data[0xA:0xE] == b"IECS":
        return "iecs"

    if data[:16] == b"\x00" * 0x10:
        return "at3"

    if data[:8] == b"THEIRSCE":
        return "theirsce"

    if data[:3] == b"MFH":
        return "mfh"

    if data[:4] == b"anp3":
        return "anp3"

    if data[:4] == b"EFFE":
        return "effe"

    # 0x####BD27 is the masked addiu sp,sp,#### mips instruction
    if data[2:4] == b"\xBD\x27":
        return "md1"

    if data[6:8] == b"\xBD\x27":
        return "md2"  # It's still md1 though

    is_pak = get_pak_type(data)
    if is_pak != None:
        return is_pak

    # Didn't match anything
    return "bin"


# ============================
#      EXTRACT FUNCTIONS
# ============================

def extract_dat(args):
    output_folder = get_directory_path(args.dat_path) + os.path.sep + "DAT"
    f = open(args.dat_path, "rb")

    pointers = get_pointers(args.elf_path)
    total_files = len(pointers)

    for i in range(total_files - 1):
        remainder = pointers[i] & LOW_BITS
        start = pointers[i] & HIGH_BITS
        end = (pointers[i + 1] & HIGH_BITS) - remainder
        f.seek(start, 0)
        size = end - start
        if size == 0:
            # Ignore 0 byte files
            continue
        data = f.read(size)
        file_name = "%05d" % i

        if is_compressed(data):
            c_type = struct.unpack("<b", data[:1])[0]
            data = comptolib.decompress_data(data)
            extension = get_extension(data)
            final_path = output_folder + "/%s/%s.%d.%s" % (
                extension.upper(),
                file_name,
                c_type,
                extension,
            )
        else:
            extension = get_extension(data)
            final_path = output_folder + "/%s/%s.%s" % (
                extension.upper(),
                file_name,
                extension,
            )

        final_path = output_folder + "/%s/%05d.%s" % (extension.upper(), i, extension)
        Path(get_directory_path(final_path)).mkdir(parents=True, exist_ok=True)
        o = open(final_path, "wb")
        o.write(data)
        o.close()
        print("Writing file %05d/%05d..." % (i, total_files), end="\r")

    f.close()


def extract_scpk():
    mkdir("SCPK")
    json_file = open("SCPK.json", "w")
    json_data = {}

    for file in os.listdir("DAT"):
        if not file.endswith("scpk"):
            continue
        f = open("DAT/%s" % file, "rb")
        header = f.read(4)
        if header != b"SCPK":
            f.close()
            continue
        mkdir("scpk/%s" % file.split(".")[0])
        index = file.split(".")[0]
        json_data[index] = {}
        f.read(4)
        files = struct.unpack("<L", f.read(4))[0]
        f.read(4)
        sizes = []
        for i in range(files):
            sizes.append(struct.unpack("<L", f.read(4))[0])
        for i in range(files):
            data = f.read(sizes[i])
            ext = "bin"
            if len(data) >= 0x10:
                if data[0xA:0xE] == b"THEI":
                    ext = "theirsce"
            if i == 0:
                ext = "mfh"
            if len(data) > 0x04:
                if get_pak_type(data) == "pak1":
                    ext = "pak1"
            fname = "scpk/%s/%02d.%s" % (file.split(".")[0], i, ext)
            o = open(fname, "wb")
            json_data[index][i] = data[0]
            o.write(data)
            o.close()
            if ext in ("mfh", "theirsce"):
                decompress_compto(fname)
                os.remove(fname)
                os.rename(fname + ".d", fname)
            # if ext in ('pak1'):
            # extract_pak1(fname)

        f.close()

    json.dump(json_data, json_file, indent=4)


def extract_theirsce():
    mkdir("TXT")
    # json_file = open('TBL.json', 'w')
    # json_data = {}
    # char_file = open('00015.bin', 'r', encoding='cp932')
    # char_index = char_file.read()
    # char_file.close()

    json_file = open("tbl.json", "r")
    json_data = json.load(json_file)
    json_file.close()

    theirsce_file = open("THEIRSCE.json", "w")
    theirsce_data = {}

    for name in os.listdir("theirsce/"):
        f = open("theirsce/" + name, "rb")
        header = f.read(8)
        if header != b"THEIRSCE":
            continue
        theirsce_data[name] = []
        pointer_block = struct.unpack("<L", f.read(4))[0]
        text_block = struct.unpack("<L", f.read(4))[0]
        fsize = os.path.getsize("theirsce/" + name)
        text_pointers = []
        addrs = []
        f.seek(pointer_block, 0)

        while f.tell() < text_block:
            b = f.read(1)
            if b == b"\xF8":
                addr = struct.unpack("<H", f.read(2))[0]
                if (addr < fsize - text_block) and (addr > 0):
                    # theirsce_data[name].append(f.tell() - 2)
                    addrs.append(f.tell() - 2)
                    text_pointers.append(addr)

        if len(text_pointers) == 0:
            continue

        o = open("txt/" + name + ".txt", "w", encoding="utf-8")
        for i in range(len(text_pointers)):
            f.seek(text_block + text_pointers[i] - 1, 0)
            b = f.read(1)
            if b != b"\x00":
                continue
            theirsce_data[name].append(addrs[i])
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

    # json.dump(json_data, json_file, indent=4)
    json.dump(theirsce_data, theirsce_file, indent=4)


def extract_mfh():
    print("Extracting mfh...")
    mkdir("MFH")
    for folder in os.listdir("scpk"):
        for name in os.listdir("scpk/" + folder):
            f = open("scpk/" + folder + "/" + name, "rb")
            f.read(4)
            pointers = []
            for i in range(0, 3):
                pointers.append(struct.unpack("<I", f.read(4))[0])
            pointers.append(os.path.getsize("scpk/" + folder + "/" + name))
            mkdir("mfh/" + folder)
            for i in range(0, 3):
                ext = ""
                if i == 0:
                    ext = "tm2"
                elif i == 1:
                    ext = "pani"
                else:
                    ext = "map"
                o = open("mfh/" + folder + "/" + "%02d.%s" % (i, ext), "wb")
                f.seek(pointers[i], 0)
                o.write(f.read(pointers[i + 1] - pointers[i]))
            break


# ============================
#      INSERT FUNCTIONS
# ============================

def pack_dat(args):
    sectors = [0]
    remainders = []
    buffer = 0

    output_dat_path = args.dat_out_path
    output_dat = open(output_dat_path, "wb")

    print("Packing files into %s..." % os.path.basename(output_dat_path))

    file_list = get_dat_folder_file_list(args.dat_folder_path)

    previous = -1
    dummies = 0

    for file in sorted(file_list, key=get_file_name):
        size = 0
        remainder = 0
        current = int(get_file_name(file))
        if current != previous + 1:
            while previous < current - 1:
                remainders.append(remainder)
                buffer += size + remainder
                sectors.append(buffer)
                previous += 1
                dummies += 1

        f = open(file, "rb")
        output_dat.write(f.read())
        size = os.path.getsize(file)
        remainder = 0x40 - (size % 0x40)
        if remainder == 0x40:
            remainder = 0
        output_dat.write(b"\x00" * remainder)
        f.close()

        remainders.append(remainder)
        buffer += size + remainder
        sectors.append(buffer)
        previous += 1

        print(
            "Writing file %05d/%05d..." % (current - dummies, len(file_list)), end="\r"
        )

    output_elf = open(args.elf_out_path, "r+b")
    output_elf.seek(POINTERS_BEGIN)

    for i in range(len(sectors) - 1):
        output_elf.write(struct.pack("<L", sectors[i] + remainders[i]))

    output_dat.close()
    output_elf.close()


def pack_scpk():
    mkdir("SCPK_PACKED")
    json_file = open("SCPK.json", "r")
    json_data = json.load(json_file)
    json_file.close()

    for name in os.listdir("theirsce_new"):
        folder = name.split("_")[0]
        if os.path.isdir("scpk/" + folder):
            sizes = []
            o = open("scpk_packed/%s.SCPK" % folder, "wb")
            data = bytearray()
            listdir = os.listdir("scpk/" + folder)
            for file in listdir:
                if os.path.isfile(os.path.join("scpk/" + folder, file)):
                    read = bytearray()
                    index = str(int(file.split(".")[0]))
                    fname = "scpk/%s/%s" % (folder, file)
                    f = open(fname, "rb")
                    ctype = json_data[folder][index]
                    if file.endswith("theirsce"):
                        if ctype != 0:
                            fname = "theirsce_new/" + name
                            compress_compto(fname, ctype)
                            comp = open(fname + ".c", "rb")
                            read = comp.read()
                            comp.close()
                            os.remove(fname + ".c")
                        else:
                            read = f.read()
                    elif file.endswith("mfh"):
                        if ctype != 0:
                            compress_compto(fname, ctype)
                            comp = open(fname + ".c", "rb")
                            read = comp.read()
                            comp.close()
                            os.remove(fname + ".c")
                        else:
                            read = f.read()
                    else:
                        read = f.read()
                    data += read
                    sizes.append(len(read))
                    f.close()

            o.write(b"\x53\x43\x50\x4B\x01\x00\x0F\x00")
            o.write(struct.pack("<L", len(sizes)))
            o.write(b"\x00" * 4)

            for i in range(len(sizes)):
                o.write(struct.pack("<L", sizes[i]))

            o.write(data)
            o.close()


def insert_theirsce():
    json_file = open("TBL.json", "r")
    theirsce_json = open("THEIRSCE.json", "r")
    table = json.load(json_file)
    theirsce_data = json.load(theirsce_json)
    json_file.close()
    theirsce_json.close()

    itable = dict([[i, struct.pack(">H", int(j))] for j, i in table.items()])
    itags = dict([[i, j] for j, i in TAGS.items()])
    inames = dict([[i, j] for j, i in NAMES.items()])
    icolors = dict([[i, j] for j, i in COLORS.items()])
    unames = []
    for i in NAMES.values():
        nam = "<" + str(i) + ">"
        unames.append(nam)
    ucolors = []
    for i in COLORS.values():
        col = "<" + str(i) + ">"
        ucolors.append(col)

    mkdir("THEIRSCE_NEW/")

    for name in os.listdir("txt_en"):
        f = open("txt_en/" + name, "r", encoding="utf8")
        name = name[:-4]
        theirsce = open("theirsce/" + name, "rb")
        o = open("theirsce_new/" + name, "wb")

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

        theirsce.seek(0xC, 0)
        pointer_block = struct.unpack("<L", theirsce.read(4))[0]
        theirsce.seek(0, 0)
        header = theirsce.read(pointer_block)
        o.write(header + b"\x00")
        theirsce.close()

        pos = 1
        for i in range(len(txts)):
            o.seek(theirsce_data[name][i], 0)
            o.write(struct.pack("<H", pos))
            pos += sizes[i]

        o.seek(pointer_block + 1, 0)

        for t in txts:
            o.write(t)
        o.close()


# ============================
#      INSERT FUNCTIONS
# ============================

def export_tbl():
    json_file = open("TBL.json", "r")
    table = json.load(json_file)
    json_file.close()
    f = open("tbl.tbl", "w", encoding="utf8")
    for k in sorted(table):
        f.write("%04X=%s\n" % (int(k), table[k]))


def extract_files(args):
    print("Extracting BIN...")
    extract_dat(args)
    # print ("Extracting SCPK...")
    # extract_scpk()
    # extract_mfh()
    # print ("Extracting script...")
    # move_theirsce()
    # extract_theirsce()


def insert_files():
    print("Inserting script...")
    insert_theirsce()
    print("Packing scpk...")
    pack_scpk()
    move_scpk_packed()


def get_arguments(argv=None):
    # Init argument parser
    parser = argparse.ArgumentParser()

    # Add arguments, obviously
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + SCRIPT_VERSION
    )

    sp = parser.add_subparsers(title="Available actions", required=True, dest="action")

    # Unpack commands
    sp_unpack = sp.add_parser(
        "unpack", help="Unpacks some file types into more useful ones."
    )
    sp_unpack.add_argument(
        "file",
        choices=["dat", "mfh", "theirsce"],
        metavar="FILE",
        help="Unpacks file containers.",
    )

    sp_unpack.add_argument(
        "--dat-path",
        metavar="DAT_PATH",
        default="DAT.BIN",
        help="Specify custom DAT.BIN file path.",
        type=os.path.abspath,
    )

    sp_unpack.add_argument(
        "--elf-path",
        metavar="ELF_PATH",
        default="SLPS_254.50",
        help="Specify custom SLPS_254.50 (a.k.a ELF) file path.",
        type=os.path.abspath,
    )

    # PAK commands
    sp_pack = sp.add_parser("pack", help="Packs some file types into the originals.")
    sp_pack.add_argument(
        "file",
        choices=["scpk", "dat", "theirsce"],
        metavar="file type",
        help="Inserts files back into their containers.",
    )

    sp_pack.add_argument(
        "--dat-out-path",
        metavar="dat_out_path",
        default="DAT.BIN",
        help="Specify custom DAT.BIN output file path.",
        type=os.path.abspath,
    )

    sp_pack.add_argument(
        "--dat-folder-path",
        metavar="dat_folder_path",
        default="DAT",
        help="Specify custom dat folder path.",
        type=os.path.abspath,
    )

    sp_pack.add_argument(
        "--elf-path",
        metavar="elf_path",
        default="SLPS_254.50",
        help="Specify custom SLPS_254.50 (a.k.a ELF) file path.",
        type=os.path.abspath,
    )

    sp_pack.add_argument(
        "--elf-out-path",
        metavar="elf_out_path",
        default="NEW_SLPS_254.50",
        help="Specify custom SLPS_254.50 (a.k.a ELF) output file path.",
        type=os.path.abspath,
    )

    # Export commands
    sp_export = sp.add_parser("export", help="Exports, I guess.")
    sp_export.add_argument(
        "file", choices=["table"], metavar="file type", help="Exports data."
    )

    return parser.parse_args(argv)


if __name__ == "__main__":
    print(
        textwrap.dedent(
            f"""\

         Tales of Rebirth DAT Extraction Tool v. {SCRIPT_VERSION}
         ----------------------------------------------
         By Alizor, SymphoniaLauren, and Ethanol
         Also Pnvnd wrote a single line of code I guess
        """
        )
    )

    args = get_arguments()
    print(vars(args))

    if args.action == "unpack":
        if args.file == "dat":
            # extract_files(args)
            extract_dat(args)
        if args.file == "mfh":
            extract_mfh()
        if args.file == "theirsce":
            extract_theirsce()

    if args.action == "pack":
        if args.file == "scpk":
            insert_files()
        if args.file == "dat":
            pack_dat(args)
        if args.file == "theirsce":
            insert_theirsce()

    if args.action == "export":
        if args.file == "table":
            export_tbl()
