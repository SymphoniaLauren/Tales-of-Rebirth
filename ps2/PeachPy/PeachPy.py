# pip install pyinstaller
# Windows Freeze: Run > cmd > pyinstaller --onefile --noconsole --icon peachpy.ico PeachPy.py

from tor import *
from tor_mov import *
from tor_pak2 import *
from tor_tmsk_tmrc import *
from unpack_folders import *

from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as box

#Prevents PC becoming hostage
from subprocess import CREATE_NO_WINDOW

#Copy SLPS file and rename to new_SLPS
from shutil import copyfile

#For Hyperlinks in the GUI
import webbrowser

def callback(url):
    webbrowser.open_new(url)

def work_dir():
    pwd = filedialog.askdirectory()
    os.chdir(pwd)
    cwd.config(text="Current Working Directory: " + pwd)

def donothing():
   filewin = Toplevel(window)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def about():
   about_win = Toplevel(window)

   about_win.title("About PeachPy")
   
   frame0 = LabelFrame(about_win, text="PeachPy GUI", padx=5, pady=5)
   frame0.pack(padx=10, pady=10)
   
   about_label = Label(frame0, text = "PeachPy is an open-source tool that can unpack and repack resources from Tales of Rebirth (PS2).")
   about_label.pack()

   link1 = Label(frame0, text="GitHub Project", fg="blue", cursor="hand2")
   link1.pack(anchor=W)
   link1.bind("<Button-1>", lambda e: callback("https://github.com/pnvnd/Tales-of-Destiny-2"))

   link2 = Label(frame0, text="Discord Server", fg="blue", cursor="hand2")
   link2.pack(anchor=W)
   link2.bind("<Button-1>", lambda e: callback("https://discord.gg/HZ2NFjpedn"))

   close_button = Button(about_win, text="Close", command = about_win.destroy)
   close_button.pack(padx=10, pady=10)

"""
Graphical Interface Start
"""

window = Tk()

window.title("PeachPy - Tales of Rebirth (PS2) Tool")

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Close", command=donothing)

filemenu.add_separator()

filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Undo", command=donothing)

editmenu.add_separator()

editmenu.add_command(label="Cut", command=donothing)
editmenu.add_command(label="Copy", command=donothing)
editmenu.add_command(label="Paste", command=donothing)
editmenu.add_command(label="Delete", command=donothing)
editmenu.add_command(label="Select All", command=donothing)

menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)

#window.iconbitmap("peachpy.ico")
label = Label(window, text = "PeachPy unpacks resources from Tales of Rebirth (PS2) and repacks them.")
#label.pack(padx = 200, pady = 50)
label.grid(row=0, column=0, columnspan=4)


#path_SLPS = Label(window, text = "Path to SLPS_251.72")
#path_SLPS.pack(anchor="w")


frame1 = LabelFrame(window, text="Unpack", padx=5, pady=5)
frame1.grid(row=1, column=0, padx=10, pady=10)

btn_unpackFPB = Button(frame1, text="Unpack FPB", command = extract_dat)
btn_unpackFPB.grid(row=0, column=0)

btn_unpackSCPK = Button(frame1, text="Unpack SCPK", command = extract_scpk)
btn_unpackSCPK.grid(row=1, column=0)

btn_unpackSCED = Button(frame1, text="Unpack SCED", command = extract_sced)
btn_unpackSCED.grid(row=2, column=0)

btn_unpackPAK1 = Button(frame1, text="Unpack PAK1", command = extract_pak1)
btn_unpackPAK1.grid(row=3, column=0)

btn_moveOUT = Button(frame1, text="Move Skits OUT", command = move_skits_out)
btn_moveOUT.grid(row=4, column=0)

btn_unpackSKIT = Button(frame1, text="Extract SKIT", command = extract_skit)
btn_unpackSKIT.grid(row=5, column=0)

frame2 = LabelFrame(window, text="Re-pack", padx=5, pady=5)
frame2.grid(row=1, column=1, padx=10, pady=10)

btn_packFPB = Button(frame2, text="Pack FPB", command = pack_dat)
btn_packFPB.grid(row=0, column=0)

btn_packSCPK = Button(frame2, text="Pack SCPK", command = pack_scpk)
btn_packSCPK.grid(row=1, column=0)

btn_packSCED = Button(frame2, text="Pack SCED", command = insert_sced)
btn_packSCED.grid(row=2, column=0)

btn_packPAK1 = Button(frame2, text="Pack PAK1", command = insert_pak1)
btn_packPAK1.grid(row=3, column=0)

btn_moveIN = Button(frame2, text="Move Skits IN", command = move_skits_in)
btn_moveIN.grid(row=4, column=0)

btn_packSKIT = Button(frame2, text="Insert SKIT", command = insert_skit)
btn_packSKIT.grid(row=5, column=0)

frame3 = LabelFrame(window, text="Misc.", padx=5, pady=5)
frame3.grid(row=1, column=2, padx=10, pady=10)

btn_sortFPB = Button(frame3, text="Organize FPB", command = unpack)
btn_sortFPB.grid(row=0, column=0)

btn_unpackMOVIE = Button(frame3, text="Unpack MOVIE", command = extract_movie)
btn_unpackMOVIE.grid(row=1, column=0)

btn_insertFONT = Button(frame3, text="Insert FONT", command = insert_font)
btn_insertFONT.grid(row=2, column=0)

btn_exportTBL = Button(frame3, text="Export TBL", command = export_tbl)
btn_exportTBL.grid(row=3, column=0)

btn_pak1skit = Button(frame3, text="Pack Movie (Broken)")
btn_pak1skit.grid(row=4, column=0)

btn_getPWD = Button(frame3, text="Change Work Directory", command = work_dir)
btn_getPWD.grid(row=5, column=0)

#Set working directory for GUI
cwd = Label(window, text = "Current Working Directory: " + os.getcwd(), bd=1, relief=SUNKEN, anchor=W)
cwd.grid(row=5, column=0, columnspan=4, sticky=W+E)



window.mainloop()
