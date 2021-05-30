# pip install pyinstaller
# Windows Freeze: Run > cmd > pyinstaller --onefile --noconsole --icon peachpy.ico PeachPy.py

from tor import *
from tor_mov import *
#from tor_pak2 import *
from tor_tmsk_tmrc import *
from unpack_folders import *

from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as box

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

def extract_scenario():
    move_theirsce()
    extract_theirsce()

def insert_scenario():
    pack_scpk()
    move_scpk_packed()


"""
Menu Bar Start
"""

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

window.resizable(False, False)

window.title("PeachPy - Tales of Rebirth (PS2) Tool")

menubar = Menu(window)

filemenu = Menu(menubar, tearoff=0)

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Change Work Directory", command= work_dir)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.destroy)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)

#window.iconbitmap("peachpy.ico")
label = Label(window, text = "PeachPy unpacks resources from Tales of Rebirth (PS2) and repacks them.")
label.grid(row=0, column=0, columnspan=4)


frame1 = LabelFrame(window, text="Unpack", padx=5, pady=5)
frame1.grid(row=1, column=0, padx=10, pady=10)

btn_unpackFPB = Button(frame1, text="Unpack DAT", command = extract_dat)
btn_unpackFPB.grid(row=0, column=0, sticky='news')

btn_unpackSCPK = Button(frame1, text="Unpack SCPK", command = extract_scpk)
btn_unpackSCPK.grid(row=1, column=0, sticky='news')

btn_THEIRSCE = Button(frame1, text="Unpack THEIRSCE", command = extract_scenario)
btn_THEIRSCE.grid(row=2, column=0, sticky='news')

btn_unpackPAK1 = Button(frame1, text="Unpack PAK1", command = extract_pak1)
btn_unpackPAK1.grid(row=3, column=0, sticky='news')

btn_unpackPAK2 = Button(frame1, text="Unpack PAK2", command = donothing)
btn_unpackPAK2.grid(row=4, column=0, sticky='news')

btn_unpackMFH = Button(frame1, text="Unpack MFH", command = extract_mfh)
btn_unpackMFH.grid(row=5, column=0, sticky='news')

frame2 = LabelFrame(window, text="Re-pack", padx=5, pady=5)
frame2.grid(row=1, column=1, padx=10, pady=10)

btn_packDAT = Button(frame2, text="Pack DAT", command = pack_dat)
btn_packDAT.grid(row=0, column=0, sticky='news')

btn_packSCPK = Button(frame2, text="Pack SCPK", command = insert_scenario)
btn_packSCPK.grid(row=1, column=0, sticky='news')

btn_packTHEIRSCE = Button(frame2, text="Pack THEIRSCE", command = insert_theirsce)
btn_packTHEIRSCE.grid(row=2, column=0, sticky='news')

btn_packPAK1 = Button(frame2, text="Pack PAK1", command = donothing)
btn_packPAK1.grid(row=3, column=0, sticky='news')

btn_packPAK2 = Button(frame2, text="Pack PAK2", command = donothing)
btn_packPAK2.grid(row=4, column=0, sticky='news')

btn_packMFH = Button(frame2, text="Pack MFH", command = donothing)
btn_packMFH.grid(row=5, column=0, sticky='news')

frame3 = LabelFrame(window, text="Misc.", padx=5, pady=5)
frame3.grid(row=1, column=2, padx=10, pady=10)

btn_sortFPB = Button(frame3, text="Sort DAT", command = unpack)
btn_sortFPB.grid(row=0, column=0, sticky='news')

btn_unpackMOVIE = Button(frame3, text="Unpack MOVIE", command = extract_mov)
btn_unpackMOVIE.grid(row=1, column=0, sticky='news')

btn_extractTMSK = Button(frame3, text="Extract TMSK", command = extract_tmsk)
btn_extractTMSK.grid(row=2, column=0, sticky='news')

btn_extractTMRC = Button(frame3, text="Extract TMRC", command = extract_tmrc)
btn_extractTMRC.grid(row=3, column=0, sticky='news')

btn_pakMOV = Button(frame3, text="Pack Movie (Broken)", command = donothing)
btn_pakMOV.grid(row=4, column=0, sticky='news')

btn_getPWD = Button(frame3, text="Export TBL", command = export_tbl)
btn_getPWD.grid(row=5, column=0, sticky='news')

"""
Status Bar Start
"""
cwd = Label(window, text = "Current Working Directory: " + os.getcwd(), bd=1, relief=SUNKEN, anchor=W)
cwd.grid(row=5, column=0, columnspan=4, sticky='news')


window.mainloop()
