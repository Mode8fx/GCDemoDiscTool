import sys
import os
from os import path, listdir
import shutil
from time import sleep
import re
from copy import copy
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askopenfilenames
import subprocess
from getpass import getpass as inputHidden
from gatelib import *

# max total content size excluding the actual demo disc: approx. 1,442,709,504 bytes; 1,408,896 KB; 1375.875 MB; 1.3436 GB

"""
TODO LIST

- Moderate - Change disc settings (time before autoplay, etc)
- Moderate - Change game header
- Mild - Add NES injection using existing app
- Mild - Add N64 injection using existing app
- Mild - Figure out how to change the format of the second+onward texture in a TPL through command line
- Meh - Logo sizes/positions may be wrong
"""

ratingArray = ["RATING_PENDING", "EARLY_CHILDHOOD", "EVERYONE", "TEEN", "ADULTS_ONLY"]

currFolder = getCurrFolder()
gcit = path.join(currFolder, "apps", "gcit.exe")
gcmtotgc = path.join(currFolder, "apps", "gcmtotgc.exe")
tgctogcm = path.join(currFolder, "apps", "tgctogcm.exe")
wimgt = path.join(currFolder, "apps", "wimgt.exe")
outputFolder = path.join(currFolder, "output")
defaultFolder = path.join(currFolder, "apps", "default files")
gbaTransferInjector = path.join(currFolder, "apps", "GCGBA_ti.py")
gbaTransferFile = path.join(currFolder, "apps", "wario_agb.tgc")
gbaEmulatorInjector = path.join(currFolder, "apps", "GCGBA_ei.py")
gbaEmulatorFile1 = path.join(currFolder, "apps", "zz_MarioVSDonkey_game.tgc")
gbaEmulatorFile2 = path.join(currFolder, "apps", "zz_MarioPinballLand_game.tgc")

tempFolder = path.join(currFolder, "temp")
tempDemoDiscFolder = path.join(tempFolder, "DemoDiscGcReEx")
tempNewAdditionsFolder = path.join(tempFolder, "NewAdditions")

contentArray = []

def main():
	Tk().withdraw()
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
	global contentArray

	contentArray = []
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
			contentArray.append(splitLine)
	cFile.close()

def prepareNewContent():
	global gbaEmulatorFile

	choice = makeChoice("Which type of content would you like to add?", ["Gamecube ISO/GCM/TGC File", "GBA ROM (for use in official emulator)", "GBA ROM (for transfer to GBA)", "Go Back"])
	if choice == 1:
		print("\nPlease select a Gamecube ISO/GCM/TGC File.")
		sleep(0.5)
		newGCGame = askopenfilename(filetypes=[("Gamecube Game File", ".iso .gcm .tgc")])
		if newGCGame == "":
			print("Action cancelled.")
			sleep(0.5)
		else:
			print("Done.")
			sleep(0.5)
			newLogo, newLogo2, newManual, newScreen = askForTextures(True)
			memcard, timer, forcereset, rating, autorunProb, argument = askForSettings(True)
			addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, forcereset, rating, autorunProb)
	elif choice == 2:
		if path.exists(gbaEmulatorFile1):
			gbaEmulatorFile = gbaEmulatorFile1
		elif path.exists(gbaEmulatorFile2):
			gbaEmulatorFile = gbaEmulatorFile2
		else:
			print("GBA emulator file not found. For more information, read '/apps/PUT MvDK OR MPL DEMO HERE.txt'")
			sleep(0.5)
			inputHidden("Action cancelled. Press Enter to continue.")
		print("\nPlease select a GBA ROM File.")
		sleep(0.5)
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			print("Action cancelled.")
			sleep(0.5)
		else:
			size = path.getsize(newGBAGame)
			if size > 16777216:
				print("This file is too big. Maximum size for GBA ROM in official emulator is 16 MB.")
				newGBAGame = ""
				sleep(0.5)
			else:
				print("Done.")
				sleep(0.5)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				memcard, timer, forcereset, rating, autorunProb, argument = askForSettings(True)
				f_02 = ""
				choice = makeChoice("Would you like to add a custom overlay to the GBA emulator app or use the existing overlay?", ["Add new overlay", "Keep current overlay"])
				if choice == 1:
					f_02 = askForFile("Select the Overlay. This is the image/texture file of the overlay surrounding the game.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: 608x448)",
						[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Overlay.")
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, forcereset, rating, autorunProb, isEmulatedGBA=True, gbaOverlay=f_02)
	elif choice == 3:
		if not path.exists(gbaTransferFile):
			print("GBA transfer file not found. For more information, read '/apps/PUT wario_agb.tgc HERE.txt'")
			sleep(0.5)
			inputHidden("Action cancelled. Press Enter to continue.")
		print("\nPlease select a GBA ROM File.")
		sleep(0.5)
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			print("Action cancelled.")
			sleep(0.5)
		else:
			size = os.path.getsize(newGBAGame)
			if size > 262144:
				print("This file is too big. Maximum size for GBA transfer is 256 KB.")
				newGBAGame = ""
				sleep(0.5)
			else:
				print("Done.")
				sleep(0.5)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				memcard, timer, forcereset, rating, autorunProb, _ = askForSettings(False)
				err, load, ind, done = askForGBATransferTextures()
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, "file://"+path.basename(newGCGame), memcard, timer, forcereset, rating, autorunProb, gbaErr=err, gbaLoad=load, gbaInd=ind, gbaDone=done)
	# else, do nothing (go back to menu)

def removeContent():
	if len(contentArray) == 0:
		print("\nThere is no content to remove.")
		sleep(0.5)
		return
	choice = makeChoice("What would you like to remove?", [c[0]+" | "+c[1]+" | "+c[2] for c in contentArray])
	try:
		os.remove(path.join(demoDiscFolder, "root", contentArray[choice-1][2]))
	except:
		print("Demo file not found.")
	try:
		shutil.rmtree(path.join(demoDiscFolder, "root", contentArray[choice-1][1]))
	except:
		print("Demo folder not found.")
	del contentArray[choice-1]
	integrateFromContentArray()
	print("Deleted content from disc.")
	sleep(1)

def buildDisc():
	global contentArray

	print("Maximum disc size: 1375.875 MB")
	discSize = getDirSize(demoDiscFolder)/1024.0/1024
	print("Disc space used: "+str(round(discSize, 3))+" MB")
	if discSize > 1375.875:
		print("\nThe contents of the extracted disc take up too much space.")
		print("If you created a screen.tpl with more than one image, and you are only a few MB over the allocated space, you may want to manually open the TPL with a program like BrawlBox and change the format of each texture to CMPR (the default is RGB5A3, which takes up more space).")
		inputHidden("Press Enter to continue.")
		return
	if len(contentArray) == 0:
		print("\nYou must add at least one game/movie to the disc before building.")
		sleep(0.5)
		inputHidden("Press Enter to continue.")
		return
	if len(contentArray) < 5:
		choice = makeChoice("You have fewer than 5 games/movies. To prevent unintended visual bugs, would you like to duplicate menu options? This will not take up any additional space.", ["Yes (Recommended)", "No"])
		if choice == 1:
			originalContentArray = copy(contentArray)
			while len(contentArray) < 5:
				contentArray += originalContentArray
			integrateFromContentArray()
	print("\nThis will build the contents of the extracted disc into a new ISO.")
	print("If you would like to manually change any contents (for example, the order of content on the menu in \"/temp/DemoDiscGcReEx/YOURDEMODISC/root/config_e/contents.txt\"), do so now.")
	choice = makeChoice("Continue?", ["Yes", "No", "Exit"])
	if choice == 2:
		return
	if choice == 3:
		sys.exit()
	createDir(outputFolder)
	while len(listdir(outputFolder)) > 0:
		print("A file already exists in "+outputFolder+". Please move, rename, or delete this file.")
		inputHidden("Press Enter to continue.")
	subprocess.call('\"'+gcit+'\" \"'+demoDiscFolder+'\" -q -d \"'+path.join(outputFolder, "output.iso")) # the name doesn't matter; gcit.exe forces a name
	input("\nCreated new ISO in "+outputFolder+".")
	inputHidden("Press Enter to exit.")
	sys.exit()

def askForTextures(isGame=True):
	newLogo1 = askForFile("Select Logo 1. This is the menu icon when the content is not highlighted.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: 267x89)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_logo.png"), "Skipped Logo 1.")
	newLogo2 = askForFile("Select Logo 2. This is the menu icon when the content is highlighted.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: 267x89)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_logo2.png"), "Skipped Logo 2.")
	newManual = askForFile("Select Manual. This is the image/texture file of the controls screen, displayed after selecting a game.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_manual.png"), "Skipped Manual.")

	print("\nSelect Screen. This is the texture file containing up to four image(s) shown on the menu.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: 340x270 for earlier discs (they show the screenshot in a smaller window), or 640x480 for most discs (the entire background changes depending on the game))")
	sleep(0.5)
	while True:
		newScreen = []
		newScreen = askopenfilenames(filetypes=[("Texture File", ".png .tpl .tex0 .bti .breft")])
		if len(newScreen) == 0:
			newScreen = [path.join(defaultFolder, "template_screen.png")]
		elif len(newScreen) > 4:
			print("You can only select up to four images.")
			continue
		elif len(newScreen) > 1 and ".tpl" in [path.splitext(s)[1] for s in newScreen]:
			print("Do not select more than 1 TPL file at a time.")
			continue
		passed = True
		for screen in newScreen:
			if not path.isfile(screen):
				print("\""+screen+"\" not found.")
				print("Skipped screen.")
				passed = False
				break
		if passed:
			print("Done.")
		break

	return newLogo1, newLogo2, newManual, newScreen

def askForGBATransferTextures():
	choice = makeChoice("Would you like to add custom textures to the GBA transfer app or use the existing textures?", ["Add new textures", "Keep current textures"])
	if choice == 2:
		return "", "", "", ""
	err = askForFile("Select the Error Screen. This is the image/texture file of the pre-transfer screen (telling you to plug in your GBA).\nIf you do not select a texture, the current texture will be used.\n(Recommended size: 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Error Screen.")
	load = askForFile("Select Loading Screen. This is the image/texture file displayed during the transfer.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Loading Screen.")
	ind = askForFile("Select Indicator Icon. This is the image/texture file of the icon that appears in the progress bar (like a dot or pill).\nIf you do not select a texture, the current texture will be used.\n(Recommended size: 30x28)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Indicator Icon.")
	done = askForFile("Select Completed Screen. This is the image/texture file displayed when a transfer finishes.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Completed Screen.")
	return err, load, ind, done

def askForSettings(askForArgument=False):
	memcard = "ON" if makeChoice("Enable use of the memory card?", ["Yes", "No"]) == 1 else "OFF"
	timer = int(makeChoiceNumInput("What should the time limit be (in minutes)? 0 = unlimited or video", 0, 999))
	forcereset = "ON" if makeChoice("What should the reset button do?", ["Reset current game/movie", "Go back to main menu (also enables START+X+B shortcut to go back to menu)"]) == 1 else "OFF"
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
	return memcard, timer, rating, forcereset, autorunProb, argument

def askForFile(description, fTypes, defaultFile, skipText):
	print("\n"+description)
	sleep(0.5)
	file = askopenfilename(filetypes=fTypes)
	if file == "":
		file = defaultFile
	if path.isfile(file):
		print("Done.")
	else:
		if file != "":
			print("\""+file+"\" not found.")
		print(skipText)
	sleep(0.5)
	return file

def addNewContent(config_att, game, logo1, logo2, manual, screen, config_argument, config_memcard, config_timer, config_forcereset, config_rating, config_autorunProb, isEmulatedGBA=False, gbaErr="", gbaLoad="", gbaInd="", gbaDone="", gbaOverlay=""):
	global contentArray

	# If the game is a GBA ROM, package and convert it to an ISO using the appropriate method
	if path.splitext(game)[1] == ".gba":
		if not isEmulatedGBA:
			gbaErrStr = ""
			if gbaErr != "":
				gbaErrStr = " --err \""+gbaErr+"\""
			gbaLoadStr = ""
			if gbaLoad != "":
				gbaLoadStr = " --load \""+gbaLoad+"\""
			gbaIndStr = ""
			if gbaInd != "":
				gbaIndStr = " --ind \""+gbaInd+"\""
			gbaDoneStr = ""
			if gbaDone != "":
				gbaDoneStr = " --done \""+gbaDone+"\""
			subprocess.call('\"'+gbaTransferInjector+'\" -a \"'+game+'\" -c \"'+gbaTransferFile+'\"'+gbaErrStr+gbaLoadStr+gbaIndStr+gbaDoneStr)
			game = path.join(currFolder, "apps", "output", listdir(path.join(currFolder, "apps", "output"))[0])
		else:
			gbaOverlayStr = ""
			if gbaOverlay != "":
				gbaOverlayStr = " -t \""+gbaOverlay+"\""
			subprocess.call('\"'+gbaEmulatorInjector+'\" -a \"'+game+'\" -c \"'+gbaEmulatorFile+'\"'+gbaOverlayStr)
			game = path.join(currFolder, "apps", "output", listdir(path.join(currFolder, "apps", "output"))[0])
	# Convert the game to TGC (if necessary) then rename+move it to the disc
	print("\nCopying game file to temp folder...")
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
		print("Deleting temp GCM...")
		os.remove(game)
		game = path.splitext(game)[0]+".tgc"
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
			print("Converting logo to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+logo1+'\" -d \"'+path.join(demoFolder, "logo.tpl")+'\" -x CMPR')
		else:
			shutil.copy(logo1, path.join(demoFolder, "logo.tpl"))
	# Convert logo2 to TPL (if necessary) then rename+move it to demo folder
	if logo2 != "":
		if path.splitext(logo2)[1] != ".tpl":
			print("Converting logo2 to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+logo2+'\" -d \"'+path.join(demoFolder, "logo2.tpl")+'\" -x CMPR')
		else:
			shutil.copy(logo2, path.join(demoFolder, "logo2.tpl"))
	# Convert manual to TPL (if necessary) then rename+move it to demo folder
	if manual != "":
		if path.splitext(manual)[1] != ".tpl":
			print("Converting manual to TPL...")
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+manual+'\" -d \"'+path.join(demoFolder, "manual.tpl")+'\" -x CMPR')
		else:
			shutil.copy(manual, path.join(demoFolder, "manual.tpl"))
	# Convert screen to TPL (if necessary) then rename+move it to demo folder
	config_screenshot ="NULL"
	if len(screen) > 0:
		config_screenshot = "screen.tpl"
		if path.splitext(screen[0])[1] != ".tpl":
			print("Converting screen to TPL in demo folder...")
			tempTPLFolder = path.join(demoFolder, "new tpl")
			createDir(tempTPLFolder)
			shutil.copy(s, path.join(tempTPLFolder, "image.png"))
			for i in range(1, len(screen)):
				shutil.copy(screen[i], path.join(tempTPLFolder, "image.mm"+str(i)+".png"))
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+path.join(tempTPLFolder, "image.png")+'\" -d \"'+path.join(demoFolder, "screen.tpl")+'\" -x CMPR') # TODO: Account for multiple screenshots here (right now it ignores anything after the first)
			shutil.rmtree(tempTPLFolder)
		else:
			shutil.copy(screen[0], path.join(demoFolder, "screen.tpl"))
	# Create appropriate config file in demo folder
	localConfFile = open(path.join(demoFolder, "local_conf.txt"), "w")
	localConfFile.writelines("<ANIMATION_FRAMES> "+str(len(screen))+"\n")
	localConfFile.writelines("<ANIMATION_INTERVAL> 120\n")
	localConfFile.writelines("<ANIMATION_SWITCHING_INTERVAL> 30\n")
	localConfFile.writelines("<ANIMATION_TYPE> FADE_IN\n")
	if config_rating == "RATING_PENDING":
		localConfFile.writelines("<RATING_INSERTION_TIME> 4\n")
		localConfFile.writelines("<RATING_INSERTION_POS> -113 58\n")
		localConfFile.writelines("<RATING_INSERTION_SIZE> 226 106\n")
	else:
		localConfFile.writelines("<RATING_INSERTION_POS> -79 110\n")
		localConfFile.writelines("<RATING_INSERTION_SIZE> 158 221\n")
	localConfFile.writelines("<END>\n")
	localConfFile.close()
	# Move demo folder to disc
	shutil.move(demoFolder, path.join(demoDiscFolder, "root", config_folder))
	# Update contentArray and integrate config file
	contentArray.append([config_att, config_folder, config_filename, config_argument, config_screenshot, config_memcard, str(config_timer), config_forcereset, config_rating, str(config_autorunProb)])
	integrateFromContentArray()
	print("\nAdded new content to extracted disc.")
	sleep(0.5)

def integrateFromContentArray():
	# newLine = config_att+"\t"+config_folder+"\t"+config_filename+"\t"+config_argument+"\t"+config_screenshot+"\t"+config_memcard+"\t"+str(config_timer)+"\t"+config_forcereset+"\t"+config_rating+"\t"+str(config_autorunProb)+"\n"
	cFile = open(contentsFile, "w")
	cFile.writelines("#att	folder			tgc_filename			argument screenshot	memcard	timer	forcereset 	rating	autorun_porbability\n")
	for content in contentArray:
		cFile.writelines("\t".join(c for c in content)+"\n")
	cFile.writelines("<END>\n")
	cFile.close()
	# Run integrate.exe (built into the demo disc)
	wd = os.getcwd()
	os.chdir(path.join(demoDiscFolder, "root", "config_e"))
	subprocess.call('\"'+integrateExe+'\"')
	os.chdir(wd)
	# Remove null characters from new integrated.txt
	with open(integratedFile, 'r+') as iFile:
		text = iFile.read()
		text = re.sub('\x00', '', text)
		iFile.seek(0)
		iFile.write(text)
		iFile.truncate()

def printOriginalContents(printHeader=True):
	print("\nCurrent demo disc contents:")
	if len(contentArray) == 0:
		print("None")
	else:
		if printHeader:
			print("TYPE    FOLDER                        FILENAME                      ARGUMENT                      MEMCARD   TIMER   ESRB RATING      AUTORUN PROB.")
		for content in contentArray:
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
	inputHidden("\nPress Enter to continue.")

if __name__ == '__main__':
	main()