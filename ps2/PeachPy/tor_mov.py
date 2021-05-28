import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string

pointer_begin = 0xE60D0
pointer_end   = 0xE6124
high_bits = 0xFFFFFFC0
low_bits = 0x3F

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

def extract_mov():
    f = open('MOV.bin', 'rb')
    mkdir('MOV')
    pointers = get_pointers()
    
    for i in range(len(pointers) - 1):
        remainder = pointers[i] & low_bits
        start = pointers[i] & high_bits
        end = (pointers[i+1] & high_bits) - remainder
        f.seek(start, 0)
        size = (end - start)
        if size == 0:
            continue
        data = f.read(size)
        extension = 'mpeg'
        o = open('MOV/' + '%05d.%s' % (i, extension), 'wb')
        o.write(data)
        o.close()

    f.close()

if __name__ == '__main__':
    if sys.argv[1] == 'unpack' and sys.argv[2] == 'mov':
        extract_mov()
    elif sys.argv[1] == 'help':
        print('Tales of Rebirth MOV.bin extraction tool\n')
        print('By SymphoniaLauren\n')
        print('USAGE:\n')
        print('python tor_mov.py [pack]/[unpack] mov\n')
        print('Currently pack mov is not supported yet oops.')
    else:
        sys.exit(1)

