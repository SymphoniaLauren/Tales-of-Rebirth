import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string

tags = {0x5: 'color', 0xB: 'name', 0xF: 'voice', 0x6: 'size', 0xC: 'item', 0xD: 'button'}
names = {1: 'Veigue', 2: 'Mao', 3: 'Eugene', 4: 'Annie', 5: 'Tytree', 6: 'Hilda',
         7: 'Claire_Agarte', 8:'Agarte_Claire', 9:'Annie (NPC)', 0x1FFF: 'OnScreenChar'}
colors = {1: 'Blue', 2: 'Red', 3: 'Purple', 4: 'Green', 5: 'Cyan', 6: 'Yellow', 7: 'White'}


pointer_begin = 0xD76B0
pointer_end   = 0xE60C8
high_bits = 0xFFFFFFC0
low_bits = 0x3F

com_tag = r'(<\w+:?\w+>)'
hex_tag = r'(\{[0-9A-F]{2}\})'

printable = ''.join((string.digits,string.ascii_letters,string.punctuation,' '))
    
def mkdir(name):
    try: os.mkdir(name)
    except: pass
    
def get_pointers():
    f = open("SLPS_254.50", 'rb')
    f.seek(pointer_begin, 0)
    pointers = []

    while f.tell() < pointer_end:
        p = struct.unpack('<L', f.read(4))[0]
        pointers.append(p)

    f.close()
    return pointers

def compress_compto(name, ctype=1):
    c = '-c%d' % ctype
    subprocess.run(['compto', c, name, name + '.c'])

def decompress_compto(name):
    subprocess.run(['compto', '-d', name, name + '.d'])

def decompress_folder(name):
    for f in os.listdir(name):
        if f.endswith('d'):
            continue
        subprocess.run(['compto', '-d', name + f, name + f + '.d'])

def extract_pak1(name):
    subprocess.run(['pakcomposer','-d', name, '-1', '-u', '-v', '-x'])

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

def is_pak0(data):
    files = struct.unpack('<I', data[:4])[0]
    index = 4
    total = 4 + files * 4
    if total > len(data):
        return False
    for i in range(files):
        size = struct.unpack('<I', data[index:index+4])[0]
        total += size
        index += 4
    if total == len(data):
        return True
    return False
    
def is_pak1(data):
    files = struct.unpack('<I', data[:4])[0]
    offset = 4 + (files * 8)
    next_byte = struct.unpack('<I', data[4:8])[0]
    if next_byte == offset:
        return True
    return False

def is_pak3(data):
    files = struct.unpack('<I', data[:4])[0]
    offset = 4 + (files * 4)
    next_byte = struct.unpack('<I', data[4:8])[0]
    if next_byte == offset:
        return True
    return False

def move_theirsce():
    mkdir('THEIRSCE')
    theirsce_dir = os.getcwd() + '/theirsce/'
    
    for folder in os.listdir('scpk'):
        if not os.path.isdir('scpk/' + folder):
            continue
        for sce in os.listdir('scpk/' + folder):
            if sce.endswith('.theirsce'):
                f = sce
                break
        new_name = '%s_%s.theirsce' % (folder, f.split('.')[0])
        shutil.copy(os.path.join('scpk',folder,f), theirsce_dir + new_name)
        print (new_name)

def move_scpk_packed():
    for f in os.listdir('scpk_packed'):
        shutil.copy(os.path.join('scpk_packed', f), 'dat/' + f)

def is_compressed(data):
    if struct.unpack('<L', data[1:5])[0] == len(data) - 9:
        return True
    return False

def get_extension(data):
    extension = 'bin'
    if data[:4] == b'SCPK':
        extension = 'scpk'
    elif data[:4] == b'TIM2':
        extension = 'tim2'
    elif data[0xB:0xE] == b'ELF':
        extension = 'irx'
    elif data[0xA:0xE] == b'IECS':
        extension = 'iecs'
    elif data[:16] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
        extension = 'at3'
    elif is_pak0(data):
        extension = 'pak0'
    elif is_pak1(data):
        extension = 'pak1'
    elif is_pak3(data):
        extension = 'pak3'
    elif data[:4] == b'anp3':
        extension = 'anp3'
    elif data[:4] == b'EFFE':
        extension = 'effe'
    else:
        pass
    return extension
    
def extract_dat():
    f = open('DAT.bin', 'rb')
    mkdir('DAT')
    #json_file = open('DAT.json', 'w')
    json_file = open('dat.json', 'r')
    #json_data = {}
    json_data = json.load(json_file)
    pointers = get_pointers()
    
    for i in range(len(pointers) - 1):
        remainder = pointers[i] & low_bits
        start = pointers[i] & high_bits
        end = (pointers[i+1] & high_bits) - remainder
        f.seek(start, 0)
        size = (end - start)
        if size == 0:
            #json_data[i] = 'dummy'
            continue
        data = f.read(size)
        #extension = get_extension(data)
        extension = json_data['%05d' % i]
        #json_data['%05d' % i] = extension
        o = open('DAT/' + '%05d.%s' % (i, extension), 'wb')
        o.write(data)
        o.close()

    #json.dump(json_data, json_file, indent=4)
    f.close()

def pack_dat():
    sectors = [0]
    remainders = []
    buffer = 0
    json_file = open('dat.json', 'r')
    json_data = json.load(json_file)
    json_file.close()
    o = open('DAT_NEW.BIN', 'wb')

    print ('Packing DAT.bin...')
    
    for k, v in json_data.items():
        size = 0
        remainder = 0
        if v != 'dummy':
            print (k)
            f = open('dat/%s.%s' % (k, v), 'rb')
            o.write(f.read())
            size = os.path.getsize('dat/%s.%s' % (k, v))
            remainder = 0x40 - (size % 0x40)
            if remainder == 0x40:
                remainder = 0
            o.write(b'\x00' * remainder)
            f.close()
        remainders.append(remainder)
        buffer += (size + remainder)
        sectors.append(buffer)

    u = open('new_SLPS_254.50', 'r+b')
    u.seek(pointer_begin)
    
    for i in range(len(sectors) - 1):
        u.write(struct.pack('<L', sectors[i] + remainders[i]))
        
    o.close()
    u.close()

def extract_scpk():
    mkdir('SCPK')
    json_file = open('SCPK.json', 'w')
    json_data = {}
    
    for file in os.listdir('DAT'):
        if not file.endswith('scpk'):
            continue
        f = open('DAT/%s' % file, 'rb')
        header = f.read(4)
        if header != b'SCPK':
            f.close()
            continue
        mkdir('scpk/%s' % file.split('.')[0])
        index = file.split('.')[0]
        json_data[index] = {}
        f.read(4)
        files = struct.unpack('<L', f.read(4))[0]
        f.read(4)
        sizes = []
        for i in range(files):
            sizes.append(struct.unpack('<L', f.read(4))[0])
        for i in range(files):
            data = f.read(sizes[i])
            ext = 'bin'
            if len(data) >= 0x10:
                if data[0xA:0xE] == b'THEI':
                    ext = 'theirsce'
            if i == 0:
                ext = 'mfh'
            if len(data) > 0x04:
                if is_pak1(data):
                    ext = 'pak1'
            fname = 'scpk/%s/%02d.%s' % (file.split('.')[0], i, ext)
            o = open(fname, 'wb')
            json_data[index][i] = data[0]
            o.write(data)
            o.close()
            if ext in ('mfh', 'theirsce'):
                decompress_compto(fname)
                os.remove(fname)
                os.rename(fname + '.d', fname)
            #if ext in ('pak1'):
                #extract_pak1(fname)

        f.close()
        
    json.dump(json_data, json_file, indent=4)

def pack_scpk():
    mkdir('SCPK_PACKED')
    json_file = open('SCPK.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    for name in os.listdir('theirsce_new'):
        folder = name.split('_')[0]
        if os.path.isdir('scpk/' + folder):
            sizes = []
            o = open('scpk_packed/%s.SCPK' % folder, 'wb')
            data = bytearray()
            listdir = os.listdir('scpk/' + folder)
            for file in listdir:
                if os.path.isfile(os.path.join('scpk/' + folder, file)):
                    read = bytearray()
                    index = str(int(file.split('.')[0]))
                    fname = 'scpk/%s/%s' % (folder, file)
                    f = open(fname, 'rb')
                    ctype = json_data[folder][index]
                    if file.endswith('theirsce'):
                        if ctype != 0:
                            fname = 'theirsce_new/' + name
                            compress_compto(fname, ctype)
                            comp = open(fname + '.c', 'rb')
                            read = comp.read()
                            comp.close()
                            os.remove(fname + '.c')
                        else:
                            read = f.read()
                    elif file.endswith('mfh'):
                        if ctype != 0:
                            compress_compto(fname, ctype)
                            comp = open(fname + '.c', 'rb')
                            read = comp.read()
                            comp.close()
                            os.remove(fname + '.c')
                        else:
                            read = f.read()
                    else:
                        read = f.read()
                    data += read
                    sizes.append(len(read))
                    f.close()
                    
            o.write(b'\x53\x43\x50\x4B\x01\x00\x0F\x00')
            o.write(struct.pack('<L', len(sizes)))
            o.write(b'\x00' * 4)
            
            for i in range(len(sizes)):
                o.write(struct.pack('<L', sizes[i]))
                
            o.write(data)
            o.close()

def extract_theirsce():
    mkdir('TXT')
    #json_file = open('TBL.json', 'w')
    #json_data = {}
    #char_file = open('00015.bin', 'r', encoding='cp932')
    #char_index = char_file.read()
    #char_file.close()

    json_file = open('tbl.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    theirsce_file = open('THEIRSCE.json', 'w')
    theirsce_data = {}
    
    for name in os.listdir('theirsce/'):
        f = open('theirsce/' + name, 'rb')
        header = f.read(8)
        if header != b'THEIRSCE':
            continue
        theirsce_data[name] = []
        pointer_block = struct.unpack('<L', f.read(4))[0]
        text_block = struct.unpack('<L', f.read(4))[0]
        fsize = os.path.getsize('theirsce/' + name)
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
        
        o = open('txt/' + name + '.txt', 'w', encoding='utf-8')
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
                            o.write("<%s:%08X>" % (tag_name, b2))
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

def insert_theirsce():
    json_file = open('TBL.json', 'r')
    theirsce_json = open('THEIRSCE.json', 'r')
    table = json.load(json_file)
    theirsce_data = json.load(theirsce_json)
    json_file.close()
    theirsce_json.close()
    
    itable = dict([[i,struct.pack('>H', int(j))] for j,i in table.items()])
    itags = dict([[i,j] for j,i in tags.items()])
    inames = dict([[i,j] for j,i in names.items()])
    icolors = dict([[i,j] for j,i in colors.items()])
    unames = []
    for i in names.values():
        nam = "<" + str(i) + ">"
        unames.append(nam)
    ucolors = []
    for i in colors.values():
        col = "<" + str(i) + ">"
        ucolors.append(col)
    
    mkdir('THEIRSCE_NEW/')

    for name in os.listdir('txt_en'):
        f = open('txt_en/' + name, 'r', encoding='utf8')
        name = name[:-4]
        theirsce = open('theirsce/' + name, 'rb')
        o = open('theirsce_new/' + name, 'wb')

        txts = []
        sizes = []
        txt = bytearray()

        for line in f:
            line = line.strip('\x0A')
            if len(line) > 0:
                if line[0] == '#':
                    continue
            if line == '[ENDBLOCK]':
                if len(line) == 0:
                    txts.append(b'\x00')
                else:
                    txts.append(txt[:-1] + b'\x00')
                sizes.append(len(txt))
                txt = bytearray()
            else:
                string_hex = re.split(hex_tag, line)
                string_hex = [sh for sh in string_hex if sh]
                for s in string_hex:
                    if re.match(hex_tag, s):
                        txt += (struct.pack('B', int(s[1:3], 16)))
                    else:
                        s_com = re.split(com_tag, s)
                        s_com = [sc for sc in s_com if sc]
                        for c in s_com:
                            if re.match(com_tag, c):
                                if ':' in c:
                                    split = c.split(':') 
                                    if split[0][1:] in itags.keys():
                                        txt += (struct.pack('B', itags[split[0][1:]]))
                                        txt += (struct.pack('<I', int(split[1][:8], 16)))
                                    else:
                                        txt += (struct.pack('B', int(split[0][1:], 16)))
                                        txt += (struct.pack('<I', int(split[1][:8], 16)))
                                if c in unames:
                                    txt += struct.pack('B', 0xB)
                                    txt += struct.pack('<I', inames[c[1:-1]])
                                if c in ucolors:
                                    txt += struct.pack('B', 0x5)
                                    txt += struct.pack('<I', icolors[c[1:-1]])
                            else:
                                for c2 in c:
                                    if c2 in itable.keys():
                                        txt += itable[c2]
                                    else:
                                        txt += c2.encode('cp932')
                txt += (b'\x01')
                
        f.close()
        
        theirsce.seek(0xC, 0)
        pointer_block = struct.unpack('<L', theirsce.read(4))[0]
        theirsce.seek(0, 0)
        header = theirsce.read(pointer_block)
        o.write(header + b'\x00')
        theirsce.close()

        pos = 1
        for i in range(len(txts)):
            o.seek(theirsce_data[name][i], 0)
            o.write(struct.pack('<H', pos))
            pos += sizes[i]

        o.seek(pointer_block + 1, 0)
        
        for t in txts:
            o.write(t)
        o.close()

def export_tbl():
    json_file = open('TBL.json', 'r')
    table = json.load(json_file)
    json_file.close()
    f = open('tbl.tbl', 'w', encoding='utf8')
    for k in sorted(table):
        f.write('%04X=%s\n' % (int(k), table[k]))

def extract_mfh():
    print ('Extracting mfh...')
    mkdir('MFH')
    for folder in os.listdir('scpk'):
        for name in os.listdir('scpk/' + folder):
            f = open('scpk/' + folder + '/' + name, 'rb')
            f.read(4)
            pointers = []
            for i in range(0, 3):
                pointers.append(struct.unpack('<I', f.read(4))[0])
            pointers.append(os.path.getsize('scpk/' + folder + '/' + name))
            mkdir('mfh/' + folder)
            for i in range(0, 3):
                ext = ''
                if i == 0: ext = 'tm2'
                elif i == 1: ext = 'pani'
                else: ext = 'map'
                o = open('mfh/' + folder + '/' + '%02d.%s' % (i, ext), 'wb')
                f.seek(pointers[i], 0)
                o.write(f.read(pointers[i+1] - pointers[i]))
            break

def extract_files():
    print ("Extracting BIN...")
    extract_dat()
    print ("Extracting SCPK...")
    extract_scpk()
    extract_mfh()
    print ("Extracting script...")
    move_theirsce()
    extract_theirsce()

def insert_files():
    print ("Inserting script...")
    insert_theirsce()
    print ("Packing scpk...")
    pack_scpk()
    move_scpk_packed()
            
if __name__ == '__main__':
    if sys.argv[1] == 'unpack':
        if sys.argv[2] == 'dat':
            extract_files()
        elif sys.argv[2] == 'mfh':
           extract_mfh()
        elif sys.argv[2] == 'theirsce':
            extract_theirsce()
    elif sys.argv[1] == 'pack':
        if sys.argv[2] == 'scpk':
            insert_files()
        elif sys.argv[2] == 'dat':
            pack_dat()
        elif sys.argv[2] == 'theirsce':
            insert_theirsce()
    elif sys.argv[1] == 'export':
        if sys.argv[2] == 'table':
            export_tbl()
    elif sys.argv[1] == 'help':
        print('Tales of Rebirth DAT Extraction Tool\n')
        print('By Alizor, SymphoniaLauren, and Ethanol\n')
        print('Also Pnvnd wrote a single line of code I guess\n')
        print('USAGE:\n')
        print('python tor.py [pack]/[unpack] [dat]/[theirsce]/[scpk]/[mfh]\n')

    else:
        sys.exit(1)
