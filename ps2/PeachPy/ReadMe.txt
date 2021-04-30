Hello, these are a collection of Tools for extracting files from Tales of Rebirth.
Code by Alizor, SymphoniaLauren, and Ethanol.
Feel free to modify these scripts as you please :-)

---tor.py---
This is the python script that extracts files from TOR's DAT.bin. It also extracts the SCPK files (containers for all of the room data in the game) the theirsce files (the scenario files of the game) and also the mfh archives (room bg graphics)
Allegedly, it should be able to reinsert files as well but SymphoniaLauren might have broken it (needs testing)

Note: needs DAT.BIN and SLPS_245.50 in the same directory. Also needs DAT.json and TBL.json in order to work.

_usage
	python tor.py 1 
	^Extracts Files^

	python tor.py 2
	^Inserts Files^

	python tor.py 3
	^Packs DAT.bin^

	python tor.py 4 
	^Extracts MFH^

	python tor.py 5
	^Extracts THEIRSCE^

	python tor.py 10
	^Exports Table^

---tor_mov.py---
Extracts movie files from MOV.bin. Currently does not support reinsertion.
Note: needs MOV.BIN and SLPS_245.50 in the same directory. 

_usage
	python tor_mov.py 1
	^Extracts Movies^

---tor_pak2.py---
Currently only extracts THEIRSCE files from PAK2 archives. No reinsert support at the moment.
NOTE: Assumes that you've organized your files using the unpack_folders.py script. Also needs TOR_TBL.json in order to work.

_usage
	python tor_pak2.py 1
	^Extracts THEIRSCE from PAK2^
	python tor_pak2.py 2
	^Extracts text from THEIRSCE^

---tor_tmsk_tmrc.py---
Converts the games custom skit image format to TIM2 files. Doesn't convert back at the moment.
NOTE: Assumes that you've organized your files using the unpack_folders.py script.

_usage
	python tor_tmsk_tmrc.py 1
	^Converts skit face to TIM2^

	python tor_tmsk_tmrc.py 2
	^Converts TMRC tiles (the moving parts of the skit image) to TIM2^

---unpack_folders.py---
Moves the files extracted from DAT.bin into folders for easy sorting

_usage
	just double click the file :-)