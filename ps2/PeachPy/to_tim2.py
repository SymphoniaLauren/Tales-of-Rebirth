import sys
import os
import struct
import re
import subprocess
import shutil
import string
import argparse
import textwrap
from pathlib import Path

#Blobby goes here
fourbap = b"bap\x00\x01" + (b"\x00" * 3) + b"\x10" + (b"\x00" * 7)
eightbap = b"bap\x00\x01" + (b"\x00" * 4) + b"\x01" + (b"\x00" * 6)
b = ".bap"

# Directory making code that we use for everything
def mkdir(name):
    try:
        os.mkdir(name)
    except:
        pass

# Converts multipaletted TIM2 to Optpix friendly TIM2 + BAP for extra palettes
def convert_tim2():
    print("Converting TIM2...")
    
    sexyfile = sys.argv[2].replace(".tm2", "")
    mkdir(sexyfile)
    o = open(sys.argv[2], "rb")
    od = o.read()
    magic = od[:4]
    bpp = od[0x23:0x24]

    #For multipaletted 4bpp TIM2
    if magic == b"TIM2" and bpp == b"\x04":
        print("TIM2 type: 4bpp")
        o.seek(0x14)
        p_len = struct.unpack("L", o.read(4))[0]
        p_num_float = p_len/0x40
        p_num = int(p_num_float)
        print("Total Number of Palettes: " + str(p_num))

        o.seek(0x18)
        idata_len = struct.unpack("<L", o.read(4))[0]

        o.seek(0x40)
        idata = o.read(idata_len)
        
        o.seek(idata_len + 0x40)
        pdata = o.read(p_len)
        
        palette_half_len = 0x20
        palette_halves = [pdata[i:i+palette_half_len] for i in range(0, len(pdata), palette_half_len)]
        palette_halves_num = p_num * 2
        phn = int(palette_halves_num)
        
        palettes = []
        
        for i in range(phn):
            if i in range(0, phn, 4):
                palette = palette_halves[i] + palette_halves[i+2]
                palettes.append(palette)
            elif i in range(1, phn, 4):
                palette = palette_halves[i] + palette_halves[i+2]
                palettes.append(palette)
            else:
                continue
        
        #Creates modified TIM2 file
        header_magic = od[0:0x10]
        header_end = od[0x20:0x40]
        n_size_int = (idata_len + 0x70)
        n_size = n_size_int.to_bytes(4, "little")
        n_idata_len = idata_len.to_bytes(4, "little")
        
        
        new_header = header_magic + n_size + b"\x40\x00\x00\x00" + n_idata_len + b"\x30\x00\x10\x00" + header_end
        n = open("Edit_" + sys.argv[2], "wb")
        n.write(new_header + idata + palettes[0])
        n.close
        
        # Creates Palette files and shoves them in a handy-dandy folder to reduce clutter
        
        for i in range(1, p_num):
            n = open(sexyfile + "/" + "palette" + "%02d" % i + ".bap", "wb")
            n.write(fourbap + palettes[i])
            n.close
        print("Conversion Successful!")
        
    # For multipaletted 8bpp TIM2
    elif magic == b"TIM2" and bpp == b"\x05":
        print("TIM2 type: 8bpp")
        o.seek(0x14)
        p_len = struct.unpack("L", o.read(4))[0]
        p_num_float = p_len/0x400
        p_num = int(p_num_float)
        print("Total Number of Palettes: " + str(p_num))

        o.seek(0x18)
        idata_len = struct.unpack("<L", o.read(4))[0]

        o.seek(0x40)
        idata = o.read(idata_len)
        
        o.seek(idata_len + 0x40)
        pdata = o.read(p_len)
        
        palette_len = 0x400
        palettes = [pdata[i:i+palette_len] for i in range(0, len(pdata), palette_len)]
        
        
        #Creates modified TIM2 file
        header_magic = od[0:0x10]
        header_end = od[0x20:0x40]
        n_size_int = (idata_len + 0x430)
        n_size = n_size_int.to_bytes(4, "little")
        n_idata_len = idata_len.to_bytes(4, "little")
        
        
        new_header = header_magic + n_size + b"\x00\x04\x00\x00" + n_idata_len + b"\x30\x00\x00\x01" + header_end
        n = open("Edit_" + sys.argv[2], "wb")
        n.write(new_header + idata + palettes[0])
        n.close
        
        #De-interleaves palettes outside of the first one and saves as .bap
        deinterleaved = []
        for i in range(1, p_num):
            pdata = palettes[i]
            palette_half_len = 0x20
            palette_halves = [pdata[i:i+palette_half_len] for i in range(0, len(pdata), palette_half_len)]
            palette_halves_num = 0x20
            phn = int(palette_halves_num)
            ptemp = []
            
            for i in range(phn):
                if i in range(0, phn, 4):
                    palette = palette_halves[i] + palette_halves[i+2]
                    ptemp.append(palette)
                elif i in range(1, phn, 4):
                    palette = palette_halves[i] + palette_halves[i+2]
                    ptemp.append(palette)
                else:
                    continue
            blobby = b"".join(ptemp)
            deinterleaved.append(blobby)
        # Creates Palette files and shoves them in a handy-dandy folder to reduce clutter
        for i in range(len(deinterleaved)):
            n = open(sexyfile + "/" + "palette" + "%02d" % i + ".bap", "wb")
            n.write(eightbap + deinterleaved[i])
            n.close
        print("Conversion Successful!")
    else:
        print("Not a valid TIM2 file REEEEEEEEEEEEEEEEEEEEEEEEE!!!!!")
        o.close

# Reinserts image data into original TIM2 file because I dont feel like fixing palettes e.e

def reinsert_idata():
    n = open("Edit_" + sys.argv[2], "rb")
    n.seek(0x18)
    idata_len = struct.unpack("<L", n.read(4))[0]
    n.seek(0x40)
    idata = n.read(idata_len)
    n.close
    
    o = open(sys.argv[2], "r+b")
    o.seek(0x40)
    o.write(idata)
    o.close
    
    print("Reinsertion Successful!")


    o.close

# This was from before I added the 8bpp deinterleaving to the main routine
# Retaining for posterity or something.

def interleave_palette():
    sexyfile = sys.argv[2].replace(".bap", "")
    p = open(sys.argv[2], "rb")
    pal = p.read()
    isbap = pal[0:3]
    if isbap != b"bap":
        print("Not a Palette reeeeee")
    elif isbap == b"bap":
        print("Interleaving palette...")
        pdata = pal[0x10:0x410]
        palette_half_len = 0x20
        palette_halves = [pdata[i:i+palette_half_len] for i in range(0, len(pdata), palette_half_len)]
        palette_halves_num = 0x20
        phn = int(palette_halves_num)
        palettes = []
        
        for i in range(phn):
            if i in range(0, phn, 4):
                palette = palette_halves[i] + palette_halves[i+2]
                palettes.append(palette)
            elif i in range(1, phn, 4):
                palette = palette_halves[i] + palette_halves[i+2]
                palettes.append(palette)
            else:
                continue
        blobby = b"".join(palettes)
        p.close
        n = open(sexyfile + "_i" + ".bap", "wb")
        n.write(eightbap + blobby)
        n.close
        print("Palette interleaved!")

if __name__ == "__main__":
    print(
        textwrap.dedent(
            f"""\

         Tales of Rebirth-Destiny TIM2 Convertor
         ----------------------------------------------
         By SymphoniaLauren
         Converts 4bpp and 8bpp TIM2 with multiple palettes to
         single paletted TIM2 and seperate .bap palette
         files for easier editing in conventional software.
         
        """
        )
    )
    if sys.argv[1] == 'convert':
        convert_tim2()
    elif sys.argv[1] == 'reinsert':
        reinsert_idata()
    elif sys.argv[1] == 'interleave':
        interleave_palette()
    elif sys.argv[1] == 'help':
        print(
            textwrap.dedent(
                f"""\

            Usage:
            python to_tim2.py convert/reinsert filename
            "convert" converts multipaletted TIM2 to single paletted TIM2, with extra palettes as seperate .bap files.
            "reinsert" reinserts edited image data into original TIM2
            Everything has to be in the same directory because I'm not that good at coding atm :,(
            
            """
            )
        )