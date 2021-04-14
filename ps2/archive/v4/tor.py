import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string

tags = {0x5: 'color', 0xB: 'name'}
names = {1: 'Veigue', 2: 'Mao', 3: 'Eugene', 4: 'Annie', 5: 'Tytree', 6: 'Hilda',
         7: 'Claire'}

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

def compress_comptoe(name, ctype=1):
    c = '-c%d' % ctype
    subprocess.run(['comptoe', c, name, name + '.c'])

def decompress_comptoe(name):
    subprocess.run(['comptoe', '-d', name, name + '.d'])

def decompress_folder(name):
    for f in os.listdir(name):
        if f.endswith('d'):
            continue
        subprocess.run(['comptoe', '-d', name + f, name + f + '.d'])

# by flame1234
def decode(param):
    a2 = param
    a3 = 0x993F
    a1 = 0x9940
    if  a3 >= a2:
        a2 = a1
    a1 = a2 >> 8
    a0 = a2 & 0xFF
    t0 = True if a1 < 0xE0 else False
    v1 = a1 - 0x40
    a3 = a0 - 1
    a2 = True if a0 < 0x80 else False
    if t0 == False:
        a1 = v1 & 0xFFFF
    t1 = a1 - 0x99
    t0 = t1 & 0xFFFF
    v0 = 0xBB
    a1 = t0 * v0
    if a2 == False:
        a0 = a3 & 0xFFFF
    t2 = True if a0 < 0x5D else False
    v1 = a0 - 1
    if t2 == False:
        a0 = v1 & 0xFFFF
    t5 = a0 - 0x40
    t4 = t5 & 0xFFFF
    t3 = a1 + t4
    v0 = t3 & 0xFFFF

    return v0

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

def move_sced():
    mkdir('SCED')
    sced_dir = os.getcwd() + '/sced/'
    
    for folder in os.listdir('scpk'):
        if not os.path.isdir('scpk/' + folder):
            continue
        for sce in os.listdir('scpk/' + folder):
            if sce.endswith('.sced'):
                f = sce
                break
        new_name = '%s_%s.sced' % (folder, f.split('.')[0])
        shutil.copy(os.path.join('scpk',folder,f), sced_dir + new_name)
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
                    ext = 'sced'
            if i == 0:
                ext = 'mfh'
            fname = 'scpk/%s/%02d.%s' % (file.split('.')[0], i, ext)
            o = open(fname, 'wb')
            json_data[index][i] = data[0]
            o.write(data)
            o.close()
            if ext in ('mfh', 'sced'):
                decompress_comptoe(fname)
                os.remove(fname)
                os.rename(fname + '.d', fname)

        f.close()
        
    json.dump(json_data, json_file, indent=4)

def pack_scpk():
    mkdir('SCPK_PACKED')
    json_file = open('SCPK.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    for name in os.listdir('sced_new'):
        folder = name.split('_')[0]
        if os.path.isdir('scpk/' + folder):
            sizes = []
            o = open('scpk_packed/%s.SCPK' % folder, 'wb')
            data = bytearray()
            listdir = os.listdir('scpk/' + folder)
            for file in listdir:
                read = bytearray()
                index = str(int(file.split('.')[0]))
                fname = 'scpk/%s/%s' % (folder, file)
                f = open(fname, 'rb')
                ctype = json_data[folder][index]
                if file.endswith('sced'):
                    if ctype != 0:
                        fname = 'sced_new/' + name
                        compress_comptoe(fname, ctype)
                        comp = open(fname + '.c', 'rb')
                        read = comp.read()
                        comp.close()
                        os.remove(fname + '.c')
                    else:
                        read = f.read()
                elif file.endswith('mfh'):
                    if ctype != 0:
                        compress_comptoe(fname, ctype)
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

def extract_sced():
    mkdir('TXT')
    #json_file = open('TBL.json', 'w')
    #json_data = {}
    #char_file = open('00015.bin', 'r', encoding='cp932')
    #char_index = char_file.read()
    #char_file.close()

    json_file = open('tbl.json', 'r')
    json_data = json.load(json_file)
    json_file.close()

    sced_file = open('SCED.json', 'w')
    sced_data = {}
    
    for name in os.listdir('sced/'):
        f = open('sced/' + name, 'rb')
        header = f.read(8)
        if header != b'THEIRSCE':
            continue
        sced_data[name] = []
        pointer_block = struct.unpack('<L', f.read(4))[0]
        text_block = struct.unpack('<L', f.read(4))[0]
        fsize = os.path.getsize('sced/' + name)
        text_pointers = []
        addrs = []
        f.seek(pointer_block, 0)
        
        while f.tell() < text_block:
            b = f.read(1)
            if b == b'\xF8':
                addr = struct.unpack('<H', f.read(2))[0]
                if (addr < fsize - text_block) and (addr > 0):
                    #sced_data[name].append(f.tell() - 2)
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
            sced_data[name].append(addrs[i])
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
                    b2 = struct.unpack('<L', f.read(4))[0]
                    if b in tags:
                        if b == 0xB and b2 in names:
                            o.write('<%s>' % names[b2])
                        else:
                            o.write('<%s:%08X>' % (tags[b], b2))
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
            o.write('\n-----------------------\n')
        f.close()
        o.close()

    #json.dump(json_data, json_file, indent=4)
    json.dump(sced_data, sced_file, indent=4)

def insert_sced():
    json_file = open('TBL.json', 'r')
    sced_json = open('SCED.json', 'r')
    table = json.load(json_file)
    sced_data = json.load(sced_json)
    json_file.close()
    sced_json.close()
    
    itable = dict([[i,struct.pack('>H', int(j))] for j,i in table.items()])
    itags = dict([[i,j] for j,i in tags.items()])
    inames = dict([[i,j] for j,i in names.items()])
    
    mkdir('SCED_NEW/')

    for name in os.listdir('txt_en'):
        f = open('txt_en/' + name, 'r', encoding='utf8')
        name = name[:-4]
        sced = open('sced/' + name, 'rb')
        o = open('sced_new/' + name, 'wb')

        txts = []
        sizes = []
        txt = bytearray()

        for line in f:
            line = line.strip('\x0A')
            if len(line) > 0:
                if line[0] == '#':
                    continue
            if line == '-----------------------':
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
                                    else:
                                        txt += (struct.pack('B', int(split[0][1:], 16)))
                                    txt += (struct.pack('<I', int(split[1][:8], 16)))
                                else:
                                    txt += struct.pack('B', 0xB)
                                    txt += struct.pack('<I', inames[c[1:-1]])
                            else:
                                for c2 in c:
                                    if c2 in itable.keys():
                                        txt += itable[c2]
                                    else:
                                        txt += c2.encode('cp932')
                txt += (b'\x01')
                
        f.close()
        
        sced.seek(0xC, 0)
        pointer_block = struct.unpack('<L', sced.read(4))[0]
        sced.seek(0, 0)
        header = sced.read(pointer_block)
        o.write(header + b'\x00')
        sced.close()

        pos = 1
        for i in range(len(txts)):
            o.seek(sced_data[name][i], 0)
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
    print ("Extracting fpb...")
    extract_dat()
    print ("Extracting scpk...")
    extract_scpk()
    extract_mfh()
    print ("Extracting script...")
    move_sced()
    extract_sced()

def insert_files():
    print ("Inserting script...")
    insert_sced()
    print ("Packing scpk...")
    pack_scpk()
    move_scpk_packed()
            
if __name__ == '__main__':
    if sys.argv[1] == '1':
        extract_files()
    elif sys.argv[1] == '2':
        insert_files()
    elif sys.argv[1] == '3':
        pack_dat()
    elif sys.argv[1] == '4':
        extract_mfh()
    elif sys.argv[1] == '10':
        export_tbl()
    elif sys.argv[1] == '?':
        print("Usage:")
        print("python tor.py 1: Extracting file requires DAT.BIN, SLPS_254.50, and comptoe.exe")
        print("python tor.py 2: Insert text from TXT_EN folder, then copy from SCPK_PACKED to DAT")
        print("python tor.py 3: Pack everything in DAT folder DAT.BIN, also requires new_SLPS_254.50")
        print("python tor.py 4: Extract MFH files")
        print("python tor.py 10: Export tbl.tbl from tbl.json to use with abcde, Cartographer, Atlas")
    else:
        sys.exit(1)
