import sys
import os
from os import path, listdir
import shutil
from time import sleep
import re
from copy import copy
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
defaultFolder = path.join(currFolder, "apps", "default files")

tempFolder = path.join(currFolder, "temp")
tempDemoDiscFolder = path.join(tempFolder, "DemoDiscGcReEx")
tempNewAdditionsFolder = path.join(tempFolder, "NewAdditions")

originalContentArray = []

def main():
	initTempFolder()
	manageDemoDisc()
	while True:
		clearScreen()
		setOriginalContents()
		printOriginalContents()
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
	global integrateExe
	global integratedFile

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
	integrateExe = path.join(demoDiscFolder, "root", "config_e", "integrate.exe")
	integratedFile = path.join(demoDiscFolder, "root", "integrated.txt")
	if path.isfile(integrateExe):
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
			memcard, timer, rating, autorunProb, argument = askForSettings(True)
			addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, rating, autorunProb)
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
				memcard, timer, rating, autorunProb, _ = askForSettings(False)
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, "file://"+path.basename(newGCGame), memcard, timer, rating, autorunProb)
	elif choice == 3:
		print("Not yet supported.")
		sleep(0.5)
	elif choice == 4:
		print("Not yet supported.")
		sleep(0.5)
	# else, do nothing (go back to menu)

def removeContent():
	print("Not yet implemented.")
	sleep(0.5)

def buildDisc():
	global originalContentArray

	if len(originalContentArray) < 5:
		choice = makeChoice("You have fewer than 5 games/movies. To prevent unintended visual bugs, would you like to duplicate menu options? This will not take up any additional space.", ["Yes, fix the bugs", "No, keep the bugs"])
		if choice == 1:
			originalOriginalContentArray = copy(originalContentArray)
			while len(originalContentArray) < 5:
				originalContentArray += originalOriginalContentArray
			integrateFromContentArray()
	print("This will build the contents of the extracted disc into a new ISO.\nIf you would like to manually change any contents (for example, the order of content on the menu in \"/temp/DemoDiscGcReEx/YOURDEMODISC/root/config_e/contents.txt\"), do so now.")
	choice = makeChoice("Continue?", ["Yes", "No", "Exit"])
	if choice == 2:
		return
	if choice == 3:
		sys.exit()
	outputISO = path.join(outputFolder, "output.iso")
	while path.isfile(outputISO):
		input("An output ISO already exists at "+outputISO+". Please move, rename, or delete this file.\nPress Enter to continue.")
	mkdir(outputFolder)
	subprocess.call('\"'+gcit+'\" \"'+demoDiscFolder+'\" -d \"'+outputISO)
	input("Created new ISO at "+outputISO+".\nPress Enter to exit.")
	sys.exit()

def askForTextures(isGame=True):
	newLogo1 = askForFile("Select Logo 1. This is the menu icon when the content is not highlighted. (Recommended size: 267x89)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_logo.png") "Skipped Logo 1.")
	newLogo2 = askForFile("Select Logo 2. This is the menu icon when the content is highlighted. (Recommended size: 267x89)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_logo2.png") "Skipped Logo 2.")
	newManual = askForFile("Select Manual. This is the image/texture file of the controls screen, displayed after selecting a game. (Recommended size: 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_manual.png") "Skipped Manual.")

	newScreen = askForFile("Select Screen. This is the texture file containing up to four image(s) shown on the menu. (Recommended size: 340x270 for earlier discs, or 640x480 for later discs)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_screen.png") "Skipped Screen.")
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

def askForSettings(askForArgument=False):
	memcard = "ON" if makeChoice("Enable use of the memory card?", ["Yes", "No"]) == 1 else "OFF"
	timer = int(makeChoiceNumInput("What should the time limit be (in minutes)? 0 = unlimited or video", 0, 999))
	rating = ratingArray[makeChoice("What is the ESRB rating?", ["Rating Pending", "Early Childhood", "Everyone", "Teen", "Mature", "Adults Only"]) - 1]
	autorunProb = int(makeChoiceNumInput("How often (0~5) should this content play on autoplay? 0=never, recommended for games; 5=often, recommended for movies", 0, 5))
	argument = "NULL"
	if askForArgument:
		choice = makeChoice("Would you like to include a special argument? This is usually only required for pre-made GBA transferrables.", ["Yes", "No (Recommended)"])
		if choice == 1:
			print("Type the argument and press Enter. If you would not like to use an argument, simply press Enter without typing anything else.")
			argument = input().strip()
			if argument == "":
				argument = "NULL"
	return memcard, timer, rating, autorunProb, argument

def askForFile(description, fTypes, defaultFile, skipText):
	print("\n"+description)
	sleep(0.5)
	Tk().withdraw()
	file = askopenfilename(filetypes=fTypes)
	if file == "":
		file = defaultFile
	if path.isfile(file):
		print("Done.")
	else:
		print("\""+file+"\" not found.")
		print(skipText)
	sleep(0.5)
	return file

def addNewContent(config_att, game, logo1, logo2, manual, screen, config_argument, config_memcard, config_timer, config_rating, config_autorunProb):
	global originalContentArray

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
	# Copy appropriate config file to demo folder
	if config_rating == "RATING_PENDING":
		shutil.copy(path.join(defaultFolder, "local_conf rating pending.txt"), path.join(demoFolder, "local_conf.txt"))
	else:
		shutil.copy(path.join(defaultFolder, "local_conf normal.txt"), path.join(demoFolder, "local_conf.txt"))
	# Move demo folder to disc
	shutil.move(demoFolder, path.join(demoDiscFolder, "root", config_folder))
	# Update originalContentArray and integrate config file
	originalContentArray.append([config_att, config_folder, config_filename, config_argument, config_screenshot, config_memcard, str(config_timer), config_forcereset, config_rating, str(config_autorunProb)])
	integrateFromContentArray()
	print("\nAdded new content to extracted disc.")
	sleep(0.5)

def integrateFromContentArray():
	# newLine = config_att+"\t"+config_folder+"\t"+config_filename+"\t"+config_argument+"\t"+config_screenshot+"\t"+config_memcard+"\t"+str(config_timer)+"\t"+config_forcereset+"\t"+config_rating+"\t"+str(config_autorunProb)+"\n"
	cFile = open(contentsFile, "w")
	cFile.writelines("#att	folder			tgc_filename			argument screenshot	memcard	timer	forcereset 	rating	autorun_porbability\n")
	for content in originalContentArray:
		cFile.writelines("\t".join(c for c in content)+"\n")
	cFile.writelines("<END>\n")
	cFile.close()
	# Run integrate.exe (built into the demo disc)
	subprocess.call('\"'+integrateExe+'\"')
	# Remove null characters from new integrated.txt
	with open(integratedFile, 'r+') as iFile:
		text = iFile.read()
		text = re.sub('\x00', '', text)
		iFile.seek(0)
		iFile.write(text)
		iFile.truncate()

def printOriginalContents(printHeader=True):
	print("\nCurrent demo disc contents:")
	if len(originalContentArray) == 0:
		print("None")
	else:
		if printHeader:
			print("TYPE    FOLDER                        FILENAME                      ARGUMENT                      MEMCARD   TIMER   ESRB RATING      AUTORUN PROB.")
		for content in originalContentArray:
			print(content[0].ljust(8)+content[1].ljust(30)+content[2].ljust(30)+content[3].ljust(30)+content[5].ljust(10)+content[6].ljust(8)+content[8].ljust(17)+content[9])

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