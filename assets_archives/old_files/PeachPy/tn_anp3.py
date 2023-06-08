import sys
import os
import json
import struct
import re
import subprocess
import shutil
import string


anp3_data = b'\x61\x6E\x70\x33\x01\x00\x00\x00\x4C\x00\x00\x00\x70\x3C\x00\x00\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x00\x00\x00\x01\x00\x00\x00\x30\x00\x00\x00\x0A\x00\x00\x00\x02\x00\x00\x00\x60\x1E\x00\x00\x50\x00\x00\x00\x00\x00\x00\x00\x50\x00\x00\x00\xB0\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
anp3_data_nol = b'\x61\x6E\x70\x33\x01\x00\x00\x00\x4C\x00\x00\x00\x70\x36\x00\x00\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x00\x00\x00\x01\x00\x00\x00\x30\x00\x00\x00\x0A\x00\x00\x00\x02\x00\x00\x00\x60\x1E\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x50\x00\x00\x00\xB0\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
tile_header = b'\xA0\x60\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
tile_header_nol = b'\x80\x60\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
blank_pal = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def construct_anp3_reg():
    print("Construction in progress...")
    input1 = sys.argv[1]
    input2 = sys.argv[2]
    output = sys.argv[3]
    f1 = open(input1, 'rb')
    d1 = f1.read()
    tile1 = d1[0x40:0x1E40]
    p1 = d1[0x1E40:0x1E60]
    p2 = d1[0x1E60:0x1E80]
    f2 = open(input2, 'rb')
    d2 = f2.read()
    tile2 = d2[0x40:0x1E40]
    o = open(output, 'wb')
    o.write(anp3_data + tile_header + tile1 + tile_header + tile2 + p1 + blank_pal + p2 + blank_pal)
    o.close
    f1.close
    f2.close
    print("All done!")

def construct_anp3_nol():
    print("Construction in progress...")
    input1 = sys.argv[1]
    input2 = sys.argv[2]
    output = sys.argv[3]
    f1 = open(input1, 'rb')
    d1 = f1.read()
    tile1 = d1[0x40:0x1E40]
    p1 = d1[0x1E40:0x1E60]
    p2 = d1[0x1E60:0x1E80]
    f2 = open(input2, 'rb')
    d2 = f2.read()
    tile2 = d2[0x40:0x1840]
    o = open(output, 'wb')
    o.write(anp3_data_nol + tile_header + tile1 + tile_header_nol + tile2 + p1 + blank_pal + p2 + blank_pal)
    o.close
    f1.close
    f2.close
    print("All done!")

if __name__ == '__main__':
    if sys.argv[1] == 'help':
        print("Tales of Rebirth Town Name anp3 Tool\n")
        print("By SymphoniaLauren" + "\n")
        print("This tool converts TIM2 graphics to ANP3 animations, but only for the town names (of course).\n")
        print("USAGE:" "\n")
        print("python tn_anp3.py Tile1.tm2 Tile2.tm2 Output.anp3 mode\n")
        print("There's only two modes, 'reg' for the normal sized graphics and 'nol' for the Nolzen graphics.\n")
        print("Image data length needs to be the same as the original anp3 tiles.\n")
        print("Also, palettes must be 16 colors (0x40 bytes) in length as well\n")
        print("Have fun!! :D")
    elif sys.argv[4] == 'reg':
        construct_anp3_reg()
    elif sys.argv[4] == 'nol':
        construct_anp3_nol()
    else:
        sys.exit(1)