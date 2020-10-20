import sys
import os
from os import path, listdir
import shutil
from time import sleep
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askopenfilenames
from gatelib import *
import subprocess

currFolder = getCurrFolder()
gcit = path.join(currFolder, "apps", "gcit.exe")
gcmtotgc = path.join(currFolder, "apps", "gcmtotgc.exe")
tgctogcm = path.join(currFolder, "apps", "tgctogcm.exe")
outputFolder = path.join(currFolder, "output")

tempFolder = path.join(currFolder, "temp")
tempDemoDiscFolder = path.join(tempFolder, "extracted demo disc")
tempNewAdditionsFolder = path.join(tempFolder, "new")

originalContentArray = []
newContentArray = []

def main():
	initTempFolder()
	manageDemoDisc()
	while True:
		clearScreen()
		printOriginalContents()
		printNewContents()
		choice = makeChoice("What would you like to do?", ["Add content to disc", "Remove content from disc", "Build disc", "Help (Contents)", "Exit"])
		if choice == 1:
			addContent()
		elif choice == 2:
			removeContent()
		elif choice == 3:
			buildDisc()
		elif choice == 4:
			printHelpContents()
		else:
			sys.exit()

def initTempFolder():
	if path.isdir(tempFolder):
		shutil.rmtree(tempFolder)
	createDir(tempFolder)
	mkdir(tempDemoDiscFolder)
	mkdir(tempNewAdditionsFolder)

def manageDemoDisc():
	global demoDiscFolder
	global contentsFile

	clearScreen()
	print("\nPlease select a Gamecube Interactive Multi-Game Demo Disc. Version 10 and later should work, but earlier discs may work, too (they are untested).")
	sleep(1)
	sourceDemoDisc = ""
	while sourceDemoDisc == "":
		Tk().withdraw()
		sourceDemoDisc = askopenfilename(filetypes=[("Gamecube Demo Discs", ".iso .gcm")])
	subprocess.call('\"'+gcit+'\" \"'+sourceDemoDisc+'\" -q -f gcreex -d \"'+tempDemoDiscFolder+'\"')
	demoDiscFolder = path.join(tempDemoDiscFolder, listdir(tempDemoDiscFolder)[0])
	contentsFile = path.join(demoDiscFolder, "root", "config_e", "contents.txt")
	if path.isfile(path.join(demoDiscFolder, "root", "config_e", "integrate.exe")):
		print("\nValid demo disc.")
		sleep(1)
		setOriginalContents()
	else:
		print("\nInvalid disc. Quitting.")
		sleep(1)
		sys.exit()

def setOriginalContents():
	global originalContentArray

	originalContentArray = []
	if not path.isfile(contentsFile):
		print("Default contents.txt not found. Creating new file.")
		cFile = open(contentsFile, "w")
		cFile.writelines("#att	folder			tgc_filename			argument screenshot	memcard	timer	forcereset 	rating	autorun_porbability") # "porbability" is a typo on official discs
		cFile.writelines("<END>")
		cFile.close()
	cFile = open(contentsFile, "r")
	print("Getting current demo disc contents...")
	lines = cFile.readlines()
	for line in lines:
		if line.startswith("<GAME>") or line.startswith("<MOVIE>"):
			sl = re.split(' |\t', line)
			splitLine = []
			for s in sl:
				if s.strip() != "":
					splitLine.append(s.strip())
			originalContentArray.append(splitLine)
	cFile.close()

def addContent():
	global newContentArray

	choice = makeChoice("Which type of content would you like to add?", ["Gamecube ISO/GCM/TGC File", "GBA ROM (for transfer to GBA)", "NES ROM (for transfer to GBA)", "Video", "Go Back"])
	if choice == 1:
		print("\nPlease select a Gamecube ISO/GCM/TGC File.")
		sleep(1)
		Tk().withdraw()
		newGCGame = askopenfilename(filetypes=[("Gamecube Game File", ".iso .gcm .tgc")])
		if newGCGame == "":
			print("Action cancelled.")
			sleep(1)
		else:
			print("Done.")
			sleep(1)
			newLogo, newLogo2, newManual, newScreen = askForTextures(True)
			newContentArray.append([newGCGame, newLogo, newLogo2, newManual, newScreen])
	elif choice == 2:
		print("\nPlease select a GBA ROM File.")
		sleep(1)
		Tk().withdraw()
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			print("Action cancelled.")
			sleep(1)
		else:
			size = os.stat(newGBAGame).st_size
			if size > 262144:
				print("This file is too big. Maximum size for GBA transfer is 256 KB.")
				newGBAGame = ""
				sleep(1)
			else:
				print("Done.")
				sleep(1)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				newContentArray.append([newGBAGame, newLogo, newLogo2, newManual, newScreen])
	elif choice == 3:
		print("Not yet supported.")
		sleep(1)
	elif choice == 4:
		print("Not yet supported.")
		sleep(1)
	# else, do nothing (go back to menu)

def askForTextures(isGame=True):
	newLogo1 = askForFile("Select Logo 1. This is the menu icon when the content is not highlighted. (Recommended size: 267x89)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Logo 1.")
	newLogo2 = askForFile("Select Logo 2. This is the menu icon when the content is highlighted. (Recommended size: 267x89)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Logo 2.")
	newManual = askForFile("Select Manual. This is the image/texture file of the controls screen, displayed after selecting a game. (Recommended size: 640x480)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Manual.")

	print("\nSelect Screen. This is the texture file containing up to four image(s) shown on the menu. (Recommended size: 340x270 for earlier discs, or 640x480 for later discs)")
	sleep(1)
	while True:
		breakOut = True
		Tk().withdraw()
		newScreen = []
		newScreen = askopenfilenames(filetypes=[("Texture File", ".png .tpl .tex0 .bti .breft")])
		if newScreen == []:
			print("Skipped Screen.")
		elif len(newScreen) > 4:
			print("You can only select up to four images.")
			breakOut = False
		elif len(newScreen) > 1 and ".tpl" in [path.splitext(s)[1] for s in newScreen]:
			print("Do not select more than 1 TPL file at a time.")
			breakOut = False
		else:
			print("Done.")
		sleep(1)
		if breakOut:
			break

	return newLogo1, newLogo2, newManual, newScreen

def askForFile(description, fTypes, skipText):
	print("\n"+description)
	sleep(1)
	Tk().withdraw()
	file = askopenfilename(filetypes=fTypes)
	if file == "":
		print(skipText)
	else:
		print("Done.")
	sleep(1)
	return file

def printOriginalContents(printHeader=True):
	print("\nCurrent demo disc contents:")
	if len(originalContentArray) == 0:
		print("None")
	else:
		if printHeader:
			print("TYPE    FOLDER                        FILENAME                      ARGUMENT                      MEMCARD   TIMER   ESRB RATING      AUTORUN PROB.")
		for content in originalContentArray:
			print(content[0].ljust(8)+content[1].ljust(30)+content[2].ljust(30)+content[3].ljust(30)+content[5].ljust(10)+content[6].ljust(8)+content[8].ljust(17)+content[9])

def printNewContents(printHeader=True):
	print("\nNew demo disc contents (not yet added):")
	if len(newContentArray) == 0:
		print("None")
	else:
		if printHeader and len(newContentArray) > 0:
			print("CONTENT                       LOGO 1                   LOGO 2                   MANUAL                   SCREEN")
		for content in newContentArray:
			print(path.basename(content[0]).ljust(30)+path.basename(content[1]).ljust(25)+path.basename(content[2]).ljust(25)+path.basename(content[3]).ljust(25)+" ".join(path.basename(c) for c in content[4]))

def printHelpContents():
	clearScreen()
	printOriginalContents()
	printNewContents()
	print("\n")
	print("\nTYPE          - The type of content (Game or Movie; GBA content counts as a game)")
	print("\nFOLDER        - The on-disc folder containing textures (logo, etc.) and content-specific configuration")
	print("\nFILENAME      - The on-disc file containing the actual game/movie")
	print("\nARGUMENT      - Special argument for specific content (e.g. the GBA ROM in GBA content); usually NULL")
	print("\nMEMCARD       - Should the memory card be enabled; usually ON for full games, OFF for everything else")
	print("\nTIMER         - The amount of time in minutes before the content auto-quits back to the menu; 0 for unlimited or movie")
	print("\nESRB RATING   - The ESRB rating")
	print("\nAUTORUN PROB. - The frequency of this content auto-playing if no buttons are pressed on the menu;")
	print("                0 (never; recommended for games) through 5 (often; recommended for movies)")
	input("\nPress Enter to continue.")

if __name__ == '__main__':
	main()