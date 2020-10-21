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

# max total content size excluding the actual demo disc: approx. 1,442,709,504 bytes; 1,408,896 KB; 1375.875 MB; 1.3436 GB

ratingArray = ["RATING_PENDING", "EARLY_CHILDHOOD", "EVERYONE", "TEEN", "ADULTS_ONLY"]

currFolder = getCurrFolder()
gcit = path.join(currFolder, "apps", "gcit.exe")
gcmtotgc = path.join(currFolder, "apps", "gcmtotgc.exe")
tgctogcm = path.join(currFolder, "apps", "tgctogcm.exe")
wimgt = path.join(currFolder, "apps", "wimgt.exe")
outputFolder = path.join(currFolder, "output")

tempFolder = path.join(currFolder, "temp")
tempDemoDiscFolder = path.join(tempFolder, "extracted demo disc")
tempNewAdditionsFolder = path.join(tempFolder, "new")

originalContentArray = []
# newContentArray = []

def main():
	initTempFolder()
	manageDemoDisc()
	while True:
		clearScreen()
		setOriginalContents()
		printOriginalContents()
		# printNewContents()
		choice = makeChoice("What would you like to do?", ["Add content to disc", "Remove content from disc", "Build disc", "Help (Contents)", "Exit"])
		if choice == 1:
			prepareNewContent()
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
	sleep(0.5)
	sourceDemoDisc = ""
	while sourceDemoDisc == "":
		Tk().withdraw()
		sourceDemoDisc = askopenfilename(filetypes=[("Gamecube Demo Discs", ".iso .gcm")])
	subprocess.call('\"'+gcit+'\" \"'+sourceDemoDisc+'\" -q -f gcreex -d \"'+tempDemoDiscFolder+'\"')
	demoDiscFolder = path.join(tempDemoDiscFolder, listdir(tempDemoDiscFolder)[0])
	contentsFile = path.join(demoDiscFolder, "root", "config_e", "contents.txt")
	if path.isfile(path.join(demoDiscFolder, "root", "config_e", "integrate.exe")):
		print("\nValid demo disc.")
		sleep(0.5)
	else:
		print("\nInvalid disc. Quitting.")
		sleep(0.5)
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

def prepareNewContent():
	# global newContentArray

	choice = makeChoice("Which type of content would you like to add?", ["Gamecube ISO/GCM/TGC File", "GBA ROM (for transfer to GBA)", "NES ROM (for transfer to GBA)", "Video", "Go Back"])
	if choice == 1:
		print("\nPlease select a Gamecube ISO/GCM/TGC File.")
		sleep(0.5)
		Tk().withdraw()
		newGCGame = askopenfilename(filetypes=[("Gamecube Game File", ".iso .gcm .tgc")])
		if newGCGame == "":
			print("Action cancelled.")
			sleep(0.5)
		else:
			print("Done.")
			sleep(0.5)
			newLogo, newLogo2, newManual, newScreen = askForTextures(True)
			# newContentArray.append([newGCGame, newLogo, newLogo2, newManual, newScreen])
			memcard, timer, rating, autorunProb = askForSettings()
			addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, "NULL", memcard, timer, rating, autorunProb)
	elif choice == 2:
		print("\nPlease select a GBA ROM File.")
		sleep(0.5)
		Tk().withdraw()
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			print("Action cancelled.")
			sleep(0.5)
		else:
			size = os.stat(newGBAGame).st_size
			if size > 262144:
				print("This file is too big. Maximum size for GBA transfer is 256 KB.")
				newGBAGame = ""
				sleep(0.5)
			else:
				print("Done.")
				sleep(0.5)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				# newContentArray.append([newGBAGame, newLogo, newLogo2, newManual, newScreen])
				memcard, timer, rating, autorunProb = askForSettings()
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, "file://"+path.basename(newGCGame), memcard, timer, rating, autorunProb)
	elif choice == 3:
		print("Not yet supported.")
		sleep(0.5)
	elif choice == 4:
		print("Not yet supported.")
		sleep(0.5)
	# else, do nothing (go back to menu)

def askForTextures(isGame=True):
	newLogo1 = askForFile("Select Logo 1. This is the menu icon when the content is not highlighted. (Recommended size: 267x89)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Logo 1.")
	newLogo2 = askForFile("Select Logo 2. This is the menu icon when the content is highlighted. (Recommended size: 267x89)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Logo 2.")
	newManual = askForFile("Select Manual. This is the image/texture file of the controls screen, displayed after selecting a game. (Recommended size: 640x480)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Manual.")

	newScreen = askForFile("Select Screen. This is the texture file containing up to four image(s) shown on the menu. (Recommended size: 340x270 for earlier discs, or 640x480 for later discs)", [("Texture File", ".png .tpl .tex0 .bti .breft")], "Skipped Screen.")
	# print("\nSelect Screen. This is the texture file containing up to four image(s) shown on the menu. (Recommended size: 340x270 for earlier discs, or 640x480 for later discs)")
	# sleep(0.5)
	# while True:
	# 	breakOut = True
	# 	Tk().withdraw()
	# 	newScreen = []
	# 	newScreen = askopenfilenames(filetypes=[("Texture File", ".png .tpl .tex0 .bti .breft")])
	# 	if newScreen == []:
	# 		print("Skipped Screen.")
	# 	elif len(newScreen) > 4:
	# 		print("You can only select up to four images.")
	# 		breakOut = False
	# 	elif len(newScreen) > 1 and ".tpl" in [path.splitext(s)[1] for s in newScreen]:
	# 		print("Do not select more than 1 TPL file at a time.")
	# 		breakOut = False
	# 	else:
	# 		print("Done.")
	# 	sleep(0.5)
	# 	if breakOut:
	# 		break

	return newLogo1, newLogo2, newManual, newScreen

def askForSettings():
	memcard = "ON" if makeChoice("Enable use of the memory card?", ["Yes", "No"]) == 1 else "OFF"
	timer = int(makeChoiceNumInput("What should the time limit be (in minutes)? 0 = unlimited or video", 0, 999))
	rating = ratingArray[makeChoice("What is the ESRB rating?", ["Rating Pending", "Early Childhood", "Everyone", "Teen", "Mature", "Adults Only"]) - 1]
	autorunProb = int(makeChoiceNumInput("How often (0~5) should this content play on autoplay? 0=never, recommended for games; 5=often, recommended for movies", 0, 5))
	return memcard, timer, rating, autorunProb

def askForFile(description, fTypes, skipText):
	print("\n"+description)
	sleep(0.5)
	Tk().withdraw()
	file = askopenfilename(filetypes=fTypes)
	if file == "":
		print(skipText)
	else:
		print("Done.")
	sleep(0.5)
	return file

def addNewContent(config_att, game, logo1, logo2, manual, screen, config_argument, config_memcard, config_timer, config_rating, config_autorunProb):
	config_forcereset = "ON"
	# Convert the game to TGC (if necessary) then rename+move it to the disc
	print("Copying game file to temp folder...")
	oldGame = game
	game = path.join(tempNewAdditionsFolder, path.basename(oldGame))
	shutil.copy(oldGame, game)
	if path.splitext(game)[1] == ".iso":
		print("Renaming copy from ISO to GCM...")
		os.rename(game, path.splitext(game)[0]+".gcm")
		game = path.splitext(game)[0]+".gcm"
	if path.splitext(game)[1] == ".gcm":
		print("Converting GCM copy to TGC...")
		subprocess.call('\"'+gcmtotgc+'\" \"'+game+'\" \"'+path.splitext(game)[0]+".tgc"+'\"')
		game = path.splitext(game)[0]+".tgc"
		print("Deleting temp GCM...")
		os.remove(oldGame)
	print("Moving TGC to demo disc...")
	config_filename = path.basename(game).replace(" ", "_")
	os.rename(game, path.join(demoDiscFolder, "root", config_filename))
	# Create demo folder
	config_folder = path.splitext(config_filename)[0]
	demoFolder = path.join(tempNewAdditionsFolder, config_folder)
	mkdir(demoFolder)
	# Convert logo1 to TPL (if necessary) then rename+move it to demo folder
	if logo1 != "":
		if path.splitext(logo1)[1] != ".tpl":
			print("Converting Logo 1 to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+logo1+'\" -d \"'+path.join(demoFolder, "logo.tpl")+'\" -x TPL')
		else:
			shutil.copy(logo1, path.join(demoFolder, "logo.tpl"))
		logo1 = path.join(demoFolder, "logo.tpl")
		print("Moving logo.tpl to demo folder...")
		os.rename(logo1, path.join(demoFolder, "logo.tpl"))
	# Convert logo2 to TPL (if necessary) then rename+move it to demo folder
	if logo2 != "":
		if path.splitext(logo2)[1] != ".tpl":
			print("Converting Logo 1 to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+logo2+'\" -d \"'+path.join(demoFolder, "logo2.tpl")+'\" -x TPL')
		else:
			shutil.copy(logo2, path.join(demoFolder, "logo2.tpl"))
		logo2 = path.join(demoFolder, "logo2.tpl")
		print("Moving logo2.tpl to demo folder...")
		os.rename(logo2, path.join(demoFolder, "logo2.tpl"))
	# Convert manual to TPL (if necessary) then rename+move it to demo folder
	if manual != "":
		if path.splitext(manual)[1] != ".tpl":
			print("Converting Logo 1 to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+manual+'\" -d \"'+path.join(demoFolder, "manual.tpl")+'\" -x TPL')
		else:
			shutil.copy(manual, path.join(demoFolder, "manual.tpl"))
		manual = path.join(demoFolder, "manual.tpl")
		print("Moving manual.tpl to demo folder...")
		os.rename(manual, path.join(demoFolder, "manual.tpl"))
	# Convert screen to TPL (if necessary) then rename+move it to demo folder
	config_screenshot = ""
	if screen != "":
		config_screenshot = "screen.tpl"
		if path.splitext(screen)[1] != ".tpl":
			print("Converting Logo 1 to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+screen+'\" -d \"'+path.join(demoFolder, "screen.tpl")+'\" -x TPL')
		else:
			shutil.copy(screen, path.join(demoFolder, "screen.tpl"))
		screen = path.join(demoFolder, "screen.tpl")
		print("Moving screen.tpl to demo folder...")
		os.rename(screen, path.join(demoFolder, "screen.tpl"))
	# Move demo folder to disc
	shutil.move(demoFolder, path.join(demoDiscFolder, "root", config_folder))
	# Update integrate config file
	newLine = config_att+"\t"+config_folder+"\t"+config_filename+"\t"+config_argument+"\t"+config_screenshot+"\t"+config_memcard+"\t"+str(config_timer)+"\t"+config_forcereset+"\t"+config_rating+"\t"+str(config_autorunProb)+"\n"
	cFile = open(contentsFile, "r")
	allLines = cFile.readlines()
	cFile.close()
	i = 0
	while i < len(allLines):
		if allLines[i].startswith("<END>"):
			allLines.insert(i, newLine)
			break
		i += 1
	cFile = open(contentsFile, "w")
	cFile.writelines(allLines)
	cFile.close()

def printOriginalContents(printHeader=True):
	print("\nCurrent demo disc contents:")
	if len(originalContentArray) == 0:
		print("None")
	else:
		if printHeader:
			print("TYPE    FOLDER                        FILENAME                      ARGUMENT                      MEMCARD   TIMER   ESRB RATING      AUTORUN PROB.")
		for content in originalContentArray:
			print(content[0].ljust(8)+content[1].ljust(30)+content[2].ljust(30)+content[3].ljust(30)+content[5].ljust(10)+content[6].ljust(8)+content[8].ljust(17)+content[9])

# def printNewContents(printHeader=True):
# 	print("\nNew demo disc contents (not yet added):")
# 	if len(newContentArray) == 0:
# 		print("None")
# 	else:
# 		if printHeader and len(newContentArray) > 0:
# 			print("CONTENT                       LOGO 1                   LOGO 2                   MANUAL                   SCREEN")
# 		for content in newContentArray:
# 			print(path.basename(content[0]).ljust(30)+path.basename(content[1]).ljust(25)+path.basename(content[2]).ljust(25)+path.basename(content[3]).ljust(25)+" ".join(path.basename(c) for c in content[4]))

def printHelpContents():
	clearScreen()
	printOriginalContents()
	# printNewContents()
	print("\n")
	print("\nTYPE          - The type of content (Game or Movie; GBA content counts as a game)")
	print("\nFOLDER        - The on-disc folder containing textures (logo, etc.) and content-specific configuration")
	print("\nFILENAME      - The on-disc file containing the actual game/movie")
	print("\nARGUMENT      - Special argument for specific content (e.g. the GBA ROM in GBA content); usually NULL")
	print("\nMEMCARD       - Should the memory card be enabled; usually ON for full games, OFF for everything else")
	print("\nTIMER         - The amount of time in minutes before the content auto-quits back to the menu; 0 for unlimited or movie")
	print("\nESRB RATING   - The ESRB rating")
	print("\nAUTORUN PROB. - The frequency of this content auto-playing if no buttons are pressed on the menu;")
	print("                  0 (never; recommended for games) through 5 (often; recommended for movies)")
	input("\nPress Enter to continue.")

if __name__ == '__main__':
	main()