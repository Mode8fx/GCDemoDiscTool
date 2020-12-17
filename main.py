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
from PIL import Image, ImageDraw, ImageFont

ratingArray = ["RATING_PENDING", "EARLY_CHILDHOOD", "EVERYONE", "TEEN", "ADULTS_ONLY"]

currFolder = getCurrFolder()
outputFolder = path.join(currFolder, "output")

gcit = path.join(currFolder, "tools", "Gamecube ISO Tool", "gcit.exe")
gcmtotgc = path.join(currFolder, "tools", "gcmtotgc.exe")
tgctogcm = path.join(currFolder, "tools", "tgctogcm.exe")
wimgt = path.join(currFolder, "tools", "Wiimms Image Tool", "wimgt.exe")
arialFont = path.join(currFolder, "tools", "arial.ttf")

gbaEmulatorInjector = path.join(currFolder, "tools", "GC-GBA EmuInjector", "GCGBA_ei.py")
gbaEmulatorFile1 = path.join(currFolder, "tools", "GC-GBA EmuInjector", "zz_MarioVSDonkey_game.tgc")
gbaEmulatorFile2 = path.join(currFolder, "tools", "GC-GBA EmuInjector", "zz_MarioPinballLand_game.tgc")
gbaTransferInjector = path.join(currFolder, "tools", "GC-GBA TransferInjector", "GCGBA_ti.py")
gbaTransferFile = path.join(currFolder, "tools", "GC-GBA TransferInjector", "wario_agb.tgc")

tempFolder = path.join(currFolder, "temp")
tempDemoDiscFolder = path.join(tempFolder, "DemoDiscGcReEx")
tempNewAdditionsFolder = path.join(tempFolder, "NewAdditions")
tempImagesFolder = path.join(tempFolder, "Images")
tempImagePath = path.join(tempImagesFolder, "image.png")

contentArray = []
useDefaultSettings = True

inputSleep = 0 # 0.5
msgSleep = 0 # 1
maxSize = 1425760.0/1024

def main():
	global discSize
	Tk().withdraw()
	manageDemoDisc()
	discSize = getDirSize(demoDiscFolder)/1024.0/1024
	while True:
		initScreen()
		setOriginalContents()
		printOriginalContents()
		choice = makeChoice("Select an option.", [
			"Add content to disc",
			"Remove content from disc",
			"Build disc",
			"Change disc settings",
			("Enable" if useDefaultSettings else "Disable")+" advanced settings",
			"Help (Contents)",
			"Credits",
			"Exit"])
		if choice == 1:
			prepareNewContent()
		elif choice == 2:
			removeContent()
		elif choice == 3:
			buildDisc()
		elif choice == 4:
			changeDiscSettings()
		elif choice == 5:
			changeDefaultContentSettings()
		elif choice == 6:
			printHelpContents()
		elif choice == 7:
			printCredits()
		else:
			clearScreen()
			sys.exit()

def initTempFolder(initNewOnly=False):
	if initNewOnly:
		if not path.isdir(tempFolder):
			createDir(tempFolder)
		if path.isdir(tempNewAdditionsFolder):
			shutil.rmtree(tempNewAdditionsFolder)
		if path.isdir(tempImagesFolder):
			shutil.rmtree(tempImagesFolder)
	else:
		if path.isdir(tempFolder):
			shutil.rmtree(tempFolder)
		createDir(tempFolder)
		mkdir(tempDemoDiscFolder)
	mkdir(tempNewAdditionsFolder)
	mkdir(tempImagesFolder)

def manageDemoDisc():
	global demoDiscFolder, demoDiscType, contentsFile, integrateExe, integratedFile
	initScreen()
	tempDDFContents = listdir(tempDemoDiscFolder)
	if path.exists(tempDemoDiscFolder) and len([f for f in tempDDFContents if path.isdir(path.join(tempDemoDiscFolder, f))]) > 0:
		demoDiscFolder = path.join(tempDemoDiscFolder, listdir(tempDemoDiscFolder)[0])
		print("You have previously started building a demo disc:")
		print(demoDiscFolder)
		choice = makeChoice("Would you like to continue it?", ["Yes, load this disc", "No, load a new ISO"])
	else:
		choice = 2
	if choice == 1:
		print(limitedString("\nAttempting to use extracted disc."))
	else:
		print("\nPlease select a Gamecube Interactive Multi-Game Demo Disc (USA).")
		sleep(msgSleep)
		sourceDemoDisc = askopenfilename(filetypes=[("Gamecube Demo Discs", ".iso .gcm")])
		if sourceDemoDisc == "":
			print("Demo disc not found.")
			sleep(inputSleep)
			inputHidden("Press Enter to exit.")
			sys.exit()
		initTempFolder()
		subprocess.call('\"'+gcit+'\" \"'+sourceDemoDisc+'\" -q -f gcreex -d \"'+tempDemoDiscFolder+'\"')
	newTempDDFContents = [f for f in listdir(tempDemoDiscFolder) if path.isdir(path.join(tempDemoDiscFolder, f)) and (not f in tempDDFContents)]
	try:
		demoDiscFolder = path.join(tempDemoDiscFolder, newTempDDFContents[0])
	except:
		pass # this will be tested at the end of this function
	contentsFile = path.join(demoDiscFolder, "root", "config_e", "contents.txt")
	integrateExe = path.join(demoDiscFolder, "root", "config_e", "integrate.exe")
	integratedFile = path.join(demoDiscFolder, "root", "integrated.txt")
	if path.isfile(integrateExe):
		print("\nValid demo disc.")
		sleep(msgSleep)
	else:
		print("\n"+limitedString("Invalid disc. If this is really a demo disc, it may be an earlier disc that does not contain the config_e folder used to generate the menu layout."))
		# Either use a later disc (Version 9 and later should work), or copy the config_e folder from a later disc and place it in +path.join(demoDiscFolder, "root")
		sleep(msgSleep)
		inputHidden("\nPress Enter to exit.")
		sys.exit()
	demoDiscType = makeChoice("Which demo disc is this?", [
		"October 2001-August 2002 / Version 7-8",
		"Version 9-13 / Preview Disc / Mario Kart Bonus Disc / Star Wars Bonus Disc",
		"Version 14-35 / Resident Evil 4 Preview Disc"])

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
	choice = makeChoice("Which type of content would you like to add?",
		["Gamecube ISO/GCM/TGC File (Game/Demo)",
		"Gamecube ISO/GCM/TGC File (Movie/Trailer)",
		"GBA ROM (for use in official emulator)",
		"GBA ROM (for transfer to GBA)",
		"N64 ROM (for use in official emulator)",
		"Go Back"])
	if choice in [1,2]:
		print("\nPlease select a Gamecube ISO/GCM/TGC File.")
		sleep(inputSleep)
		newGCGame = askopenfilename(filetypes=[("Gamecube Game File", ".iso .gcm .tgc")])
		if newGCGame == "":
			print("\nAction cancelled.")
			sleep(msgSleep)
		else:
			print("Done.")
			sleep(msgSleep)
			isGame = (choice == 1)
			newLogo, newLogo2, newManual, newScreen = askForTextures(isGame)
			memcard, timer, forcereset, rating, autorunProb, argument = askForSettings(True)
			addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, forcereset, rating, autorunProb)
	elif choice == 3:
		if path.exists(gbaEmulatorFile1):
			gbaEmulatorFile = gbaEmulatorFile1
		elif path.exists(gbaEmulatorFile2):
			gbaEmulatorFile = gbaEmulatorFile2
		else:
			print("\n"+limitedString("GBA emulator file not found. For more information, read '/tools/GC-GBA EmuInjector/PUT MvDK OR MPL DEMO HERE.txt'"))
			sleep(inputSleep)
			inputHidden("Action cancelled. Press Enter to continue.")
			return
		print("\nPlease select a GBA ROM File.")
		sleep(msgSleep)
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			inputHidden("Action cancelled. Press Enter to continue.")
		else:
			size = path.getsize(newGBAGame)
			if size > 16777216:
				print("This file is too big. Maximum size for GBA ROM in official emulator is 16 MB.")
				newGBAGame = ""
				sleep(msgSleep)
			else:
				print("Done.")
				sleep(msgSleep)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				memcard, timer, forcereset, rating, autorunProb, argument = askForSettings(True)
				f_02 = None
				choice = makeChoice(limitedString("Would you like to add a custom overlay to the GBA emulator app or use the existing overlay?"), ["Add new overlay", "Keep current overlay"])
				if choice == 1:
					f_02 = askForFile("Select the Overlay. This is the image/texture file of the overlay surrounding the game.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: at least 608x448)",
						[("Texture File", ".png .tpl .tex0 .bti .breft")], (608, 448), "Skipped Overlay.")
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, forcereset, rating, autorunProb, isEmulatedGBA=True, gbaOverlay=f_02)
	elif choice == 4:
		if not path.exists(gbaTransferFile):
			print("\n"+limitedString("GBA transfer file not found. For more information, read '/tools/GC-GBA TransferInjector/PUT wario_agb.tgc HERE.txt'"))
			sleep(inputSleep)
			inputHidden("Action cancelled. Press Enter to continue.")
		print("\nPlease select a GBA ROM File.")
		sleep(msgSleep)
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			print("\nAction cancelled.")
			sleep(msgSleep)
		else:
			size = os.path.getsize(newGBAGame)
			if size > 262144:
				print("This file is too big. Maximum size for GBA transfer is 256 KB.")
				newGBAGame = ""
				inputHidden("Action cancelled. Press Enter to continue.")
			else:
				print("Done.")
				sleep(msgSleep)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				memcard, timer, forcereset, rating, autorunProb, _ = askForSettings(False)
				err, load, ind, done = askForGBATransferTextures()
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, "file://"+path.basename(newGCGame), memcard, timer, forcereset, rating, autorunProb, gbaErr=err, gbaLoad=load, gbaInd=ind, gbaDone=done)
	elif choice == 5:
		print("\nTo inject an N64 ROM, use the GCM N64 ROMS Injector.")
		print("https://github.com/sizious/gcm-n64-roms-injector")
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
	# else, do nothing (go back to menu)

def removeContent():
	if len(contentArray) == 0:
		print("\nThere is no content to remove.")
		sleep(msgSleep)
		inputHidden("Press Enter to continue.")
		return
	choice = makeChoice("What would you like to remove?", [c[0]+" | "+c[1]+" | "+c[2] for c in contentArray]+["Go Back"])
	if choice == len(contentArray) + 1:
		print("\nAction cancelled.")
		sleep(1)
		return
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
	print("\nDeleted content from disc.")
	sleep(1)

def buildDisc():
	global contentArray
	if discSize > maxSize:
		print("\nThe contents of the extracted disc take up too much space.")
		print(limitedString("If you created a screen.tpl with more than one image, and you are only a few MB over the allocated space, you may want to manually open the TPL with a program like BrawlBox and change the format of each texture to CMPR (the default is RGB5A3, which takes up more space)."))
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
		return
	if len(contentArray) == 0:
		print("\nYou must add at least one game/movie to the disc before building.")
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
		return
	if len(contentArray) < 5:
		choice = makeChoice(limitedString("You have fewer than 5 games/movies. To prevent unintended visual bugs, would you like to duplicate menu options? This will not take up any additional space."), ["Yes (Recommended)", "No"])
		if choice == 1:
			originalContentArray = copy(contentArray)
			while len(contentArray) < 5:
				contentArray += originalContentArray
			integrateFromContentArray()
	askForIDAndName()
	# Finalize
	print("\nThis will build the contents of the extracted disc into a new ISO.")
	print(limitedString("If you would like to manually change any contents (for example, the order of content on the menu in \""+demoDiscFolder+"/root/config_e/contents.txt\"), do so now."))
	choice = makeChoice("Continue?", ["Yes", "No, go back", "Quit"])
	if choice == 2:
		return
	if choice == 3:
		sys.exit()
	createDir(outputFolder)
	while len(listdir(outputFolder)) > 0:
		print(limitedString("A file already exists in "+outputFolder+". Please move, rename, or delete this file."))
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
	subprocess.call('\"'+gcit+'\" \"'+demoDiscFolder+'\" -q -d \"'+path.join(outputFolder, "output.iso")) # the name doesn't matter; gcit.exe forces a name
	print("\n"+limitedString("Created new ISO in "+outputFolder+"."))
	sleep(msgSleep)
	print(limitedString("The currently extracted disc is stored in \""+demoDiscFolder+"\". Delete this folder if you are done building your disc."))
	sleep(msgSleep)
	inputHidden("Press Enter to exit.")
	sys.exit()

def askForTextures(isGame=True):
	if demoDiscType == 1:
		logoSize = None
		manualSize = (582, 276) if isGame else None
		manualStr = "582x276" if isGame else None
		screenshotSize = (145, 190)
		screenshotStr = "145x190"
	else:
		logoSize = (276, 89)
		logoStr = "276,89"
		manualSize = (640, 480) if isGame else None
		manualStr = "640x480" if isGame else None
		screenshotSize = (340, 270) if demoDiscType == 2 else (456, 342)
		screenshotStr = "340x270" if demoDiscType == 2 else "456x342"
	newLogo1 = None
	newLogo2 = None
	newManual = None
	newScreen = None
	if logoSize is not None:
		newLogo1 = askForFile("Select Logo 1. This is the menu icon when the content is not highlighted. If you do not select a texture, a default single-color texture with the game's name will be used. (Recommended size: at least "+logoStr+")",
			[("Texture File", ".png .tpl .tex0 .bti .breft")], logoSize, "Skipped Logo 1.")
		newLogo2 = askForFile("Select Logo 2. This is the menu icon when the content is highlighted. If you do not select a texture, a default single-color texture with the game's name will be used. (Recommended size: at least "+logoStr+")",
			[("Texture File", ".png .tpl .tex0 .bti .breft")], logoSize, "Skipped Logo 2.")
	if manualSize is not None:
		newManual = askForFile("Select Manual. This is the image/texture file of the controls screen, displayed after selecting a game. If you do not select a texture, a default single-color texture will be used. (Recommended size: at least 640x480)",
			[("Texture File", ".png .tpl .tex0 .bti .breft")], manualSize, "Skipped Manual.")

	print("\n"+limitedString("Select Screen. This is the texture file containing up to four image(s) shown on the menu. If you do not select a texture, a default single-color texture will be used. (Recommended size: at least "+screenshotStr+")"))
	print(limitedString("When selecting multiple images, hold CTRL while clicking and select the images IN REVERSE ORDER."))
	sleep(inputSleep)
	while True:
		newScreen = []
		newScreen = list(askopenfilenames(filetypes=[("Texture File", ".png .tpl .tex0 .bti .breft")]))
		if len(newScreen) == 0:
			newScreen = screenshotSize
		elif len(newScreen) > 4:
			print("You can only select up to four images.")
			continue
		elif len(newScreen) > 1 and ".tpl" in [path.splitext(s)[1] for s in newScreen]:
			print("Do not select more than 1 TPL file at a time.")
			continue
		passed = True
		for screen in newScreen:
			if not path.isfile(screen):
				print(limitedString("\""+screen+"\" not found."))
				print("Skipped screen.")
				passed = False
				break
		if passed:
			print("Done.")
		break

	return newLogo1, newLogo2, newManual, newScreen

def askForGBATransferTextures():
	choice = makeChoice(limitedString("Would you like to add custom textures to the GBA transfer app or use the existing textures?"), ["Add new textures", "Keep current textures"])
	if choice == 2:
		return "", "", "", ""
	err = askForFile("Select the Error Screen. This is the image/texture file of the pre-transfer screen (telling you to plug in your GBA).\nIf you do not select a texture, the current texture will be used.\n(Recommended size: at least 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Error Screen.")
	load = askForFile("Select Loading Screen. This is the image/texture file displayed during the transfer.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: at least 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Loading Screen.")
	ind = askForFile("Select Indicator Icon. This is the image/texture file of the icon that appears in the progress bar (like a dot or pill).\nIf you do not select a texture, the current texture will be used.\n(Recommended size: at least 30x28)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Indicator Icon.")
	done = askForFile("Select Completed Screen. This is the image/texture file displayed when a transfer finishes.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: at least 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Completed Screen.")
	return err, load, ind, done

def askForSettings(askForArgument=False):
	if useDefaultSettings:
		memcard = "ON"
		timer = 0
		forcereset = "OFF"
		rating = ratingArray[makeChoice("What is the ESRB rating?", ["Rating Pending", "Early Childhood", "Everyone", "Teen", "Mature", "Adults Only"]) - 1]
		autorunProb = "5"
		argument = "NULL"
	else:
		memcard = "ON" if makeChoice("Enable use of the memory card?", ["Yes", "No"]) == 1 else "OFF"
		timer = int(makeChoiceNumInput("What should the time limit be (in minutes)? 0 = unlimited or movie", 0, 999))
		# forcereset = "ON" if makeChoice("What should the reset button do?", ["Reset current game/movie", "Go back to main menu"]) == 1 else "OFF"
		forcereset = "OFF" # actually, I'm not sure what forcereset does...
		rating = ratingArray[makeChoice("What is the ESRB rating?", ["Rating Pending", "Early Childhood", "Everyone", "Teen", "Mature", "Adults Only"]) - 1]
		autorunProb = int(makeChoiceNumInput(limitedString("How often (0~5) should this content play on autoplay? 0=never, recommended for games; 5=often, recommended for movies"), 0, 5))
		argument = "NULL"
		if askForArgument:
			choice = makeChoice(limitedString("Would you like to include a special argument? This is usually only required for pre-made GBA transferrables."), ["Yes", "No (Recommended)"])
			if choice == 1:
				print(limitedString("Type the argument and press Enter. If you would not like to use an argument, simply press Enter without typing anything else."))
				argument = input().strip()
				if argument == "":
					argument = "NULL"
	return memcard, timer, forcereset, rating, autorunProb, argument

def askForFile(description, fTypes, defaultFile, skipText):
	print("\n"+limitedString(description))
	sleep(inputSleep)
	file = askopenfilename(filetypes=fTypes)
	if file == "":
		file = defaultFile
		print(skipText)
		sleep(msgSleep)
		return file
	if path.isfile(file):
		print("Done.")
	else:
		if file != "":
			print(limitedString("\""+file+"\" not found."))
		print(skipText)
	sleep(msgSleep)
	return file

def addNewContent(config_att, game, logo1, logo2, manual, screen, config_argument, config_memcard, config_timer, config_forcereset, config_rating, config_autorunProb, isEmulatedGBA=False, gbaErr="", gbaLoad="", gbaInd="", gbaDone="", gbaOverlay=None):
	global contentArray
	createDir(tempImagesFolder)
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
			game = path.join(currFolder, "tools", "output", listdir(path.join(currFolder, "tools", "output"))[0])
		else:
			gbaOverlayStr = ""
			if gbaOverlay is not None:
				if isinstance(gbaOverlay, str):
					gbaOverlayStr = " -t \""+gbaOverlay+"\""
				else:
					img = Image.new('RGB', logo2, color = (153, 217, 234))
					img.save(tempImagePath)
					gbaOverlayStr = " -t \""+tempImagePath+"\""
			subprocess.call('\"'+gbaEmulatorInjector+'\" -a \"'+game+'\" -c \"'+gbaEmulatorFile+'\"'+gbaOverlayStr)
			game = path.join(currFolder, "tools", "output", listdir(path.join(currFolder, "tools", "output"))[0])
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
	finalLogo1Path = path.join(demoFolder, "logo.tpl")
	finalLogo2Path = path.join(demoFolder, "logo2.tpl")
	finalManualPath = path.join(demoFolder, "manual.tpl")
	finalScreenPath = path.join(demoFolder, "screenshot.tpl" if demoDiscType == 1 else "screen.tpl")
	gameName = ""
	if isinstance(logo1, tuple) or isinstance(logo2, tuple):
		gameName = input("What is the name of this game (what should be written on the default logo icon)?")
	# Convert logo1 to TPL (if necessary) then rename+move it to demo folder
	addTPL(logo1, "logo", finalLogo1Path, (34, 177, 76), gameName)
	# Convert logo2 to TPL (if necessary) then rename+move it to demo folder
	addTPL(logo2, "logo2", finalLogo2Path, (181, 230, 29), gameName)
	# Convert manual to TPL (if necessary) then rename+move it to demo folder
	addTPL(manual, "manual", finalManualPath, (195, 195, 195), None)
	# Convert screen to TPL (if necessary) then rename+move it to demo folder
	if isinstance(screen, list):
		if path.splitext(screen[0])[1] != ".tpl":
			print("Converting screen to TPL in demo folder...")
			tempTPLFolder = path.join(demoFolder, "new tpl")
			createDir(tempTPLFolder)
			shutil.copy(screen[0], path.join(tempTPLFolder, "image.png"))
			for i in range(1, len(screen)):
				shutil.copy(screen[i], path.join(tempTPLFolder, "image.mm"+str(i)+".png"))
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+path.join(tempTPLFolder, "image.png")+'\" -d \"'+path.join(demoFolder, "screen.tpl")+'\" -x CMPR')
			shutil.rmtree(tempTPLFolder)
		else:
			shutil.copy(screen[0], path.join(demoFolder, "screen.tpl"))
	else:
		print("Converting default screen to TPL...")
		img = Image.new('RGB', screen, color=(153, 217, 234))
		img.save(tempImagePath)
		subprocess.call('\"'+wimgt+'\" ENCODE \"'+tempImagePath+'\" -d \"'+finalScreenPath+'\" -x CMPR')
	shutil.rmtree(tempImagesFolder)
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
	contentArray.append([config_att, config_folder, config_filename, config_argument, "screen.tpl", config_memcard, str(config_timer), config_forcereset, config_rating, str(config_autorunProb)])
	integrateFromContentArray()
	print("\nAdded new content to extracted disc.")
	sleep(inputSleep)
	inputHidden("Press Enter to continue.")

def addTPL(original, originalType, finalPath, col=(128,128,128), text=None):
	if original is not None:
		if isinstance(original, str):
			if path.splitext(original)[1] != ".tpl":
				print("Converting "+originalType+" to TPL...")
				subprocess.call('\"'+wimgt+'\" ENCODE \"'+original+'\" -d \"'+finalPath+'\" -x CMPR')
			else:
				shutil.copy(original, finalPath)
		else:
			print("Converting default "+originalType+" to TPL...")
			img = Image.new('RGB', original, color=col)
			if text is not None:
				fnt = ImageFont.truetype(arialFont, 24)
				imgText = ImageDraw.Draw(img)
				textLength, textHeight = fnt.getsize(text)
				if textLength < original[0]*.9:
					imgText.text(((original[0]-textLength)/2, (original[1]-textHeight)/2), text, font=fnt, fill=(255, 255, 255))
				else:
					textArray = splitStringIntoParts(text, 2, True)
					if all(fnt.getsize(t)[0] < original[0]*.9 for t in textArray):
						textLength, textHeight = fnt.getsize(textArray[0])
						imgText.text(((original[0]-textLength)/2, (original[1]-textHeight)/2), textArray[0], font=fnt, fill=(255, 255, 255))
						textLength, textHeight = fnt.getsize(textArray[1])
						imgText.text(((original[0]-textLength)/2, (original[1]+textHeight)/2), textArray[1], font=fnt, fill=(255, 255, 255))
					else:
						textArray = splitStringIntoParts(text, 3, True)
						textLength, textHeight = fnt.getsize(textArray[0])
						imgText.text(((original[0]-textLength)/2, (original[1]/2)-(textHeight*1.5)), textArray[0], font=fnt, fill=(255, 255, 255))
						textLength, textHeight = fnt.getsize(textArray[1])
						imgText.text(((original[0]-textLength)/2, (original[1]/2)-(textHeight*.5)), textArray[1], font=fnt, fill=(255, 255, 255))
						textLength, textHeight = fnt.getsize(textArray[2])
						imgText.text(((original[0]-textLength)/2, (original[1]/2)+(textHeight*.5)), textArray[2], font=fnt, fill=(255, 255, 255))
			img.save(tempImagePath)
			subprocess.call('\"'+wimgt+'\" ENCODE \"'+tempImagePath+'\" -d \"'+finalPath+'\" -x CMPR')

def integrateFromContentArray():
	global discSize
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
	discSize = getDirSize(demoDiscFolder)/1024.0/1024

def askForIDAndName():
	bootFile = open(path.join(demoDiscFolder, "sys", "boot.bin"), "r+b")
	print("\nCurrent Disc:")
	bootFile.seek(0x0)
	print("ID: "+bootFile.read(6).decode('utf-8'))
	bootFile.seek(0x20)
	print("Name: "+bootFile.read(63).decode('utf-8'))
	choice = makeChoice(limitedString("Would you like to change the ID/Name? Having a unique ID/Name is important for certain ISO loaders."), ["Yes", "No"])
	if choice == 1:
		print("\n"+limitedString("Input the new ID and press Enter. If you do not want to change the ID, press Enter without typing anything else."))
		print(limitedString("It is strongly recommended that the ID is six characters long and follows this naming convention: (letter)(letter)(letter)(region letter)(number)(number), where (region letter) is E (USA), P (PAL), or J (Japan) depending on the region. Example: SNQE12"))
		new = input().strip().upper()
		if new != "":
			bootFile.seek(0x0)
			bootFile.write(bytes(new, 'utf-8'))
			for _ in range(6-len(new)):
				bootFile.write(bytes([0x00]))
		print("\n"+limitedString("Input the new name and press Enter. If you do not want to change the ID, press Enter without typing anything else."))
		print(limitedString("The name should be a maximum of 63 characters long. Anything more will be ignored."))
		new = input().strip()
		if new != "":
			bootFile.seek(0x20)
			bootFile.write(bytes(new[:min(len(new), 63)], 'utf-8'))
			for _ in range(63-len(new)):
				bootFile.write(bytes([0x00]))
		print("\nID and Name changed to the following:")
		bootFile.seek(0x0)
		print("ID: "+bootFile.read(6).decode('utf-8'))
		bootFile.seek(0x20)
		print("Name: "+bootFile.read(63).decode('utf-8'))
	bootFile.close()

def changeDiscSettings():
	choice = makeChoice("Which setting would you like to change?",
		["Timer (the amount of time before a random game/movie autoplays; default = 15 seconds)", "Banner (the disc banner that appears in the system menu)", "Go Back"])
	if choice == 1:
		num = makeChoiceNumInput("How many seconds would you like to wait before autoplay activates? (0 = disable autoplay)", 0, 999)
		systemFile = open(path.join(demoDiscFolder, "root", "config_e", "system.txt"), "w")
		systemFile.writelines("<PURPOSE> sales-promotion\n")
		systemFile.writelines("<TIMER> "+str(num)+"\n")
		systemFile.writelines("<START_TIMING> AT_ONCE\n")
		systemFile.writelines("<WAIT> 0\n")
		systemFile.writelines("<END>\n")
		systemFile.close()
		print("Changed timer.")
		sleep(msgSleep)
	elif choice == 2:
		choice = makeChoice(limitedString("Would you like to replace the current banner? You must provide a banner that is already in a .bnr format."), ["Yes", "No"])
		if choice == 1:
			newBanner = askopenfilename(filetypes=[("Banner File", ".bnr")])
			if newBanner == "":
				print("\nAction cancelled.")
				sleep(msgSleep)
			else:
				os.remove(path.join(demoDiscFolder, "root", "opening.bnr"))
				shutil.copy(newBanner, path.join(demoDiscFolder, "root", "opening.bnr"))
				print("Replaced banner.")
				sleep(msgSleep)
		else:
			print("\nAction cancelled.")
			sleep(msgSleep)
	inputHidden("Press Enter to continue.")

def changeDefaultContentSettings():
	global useDefaultSettings
	if useDefaultSettings:
		print("\nDefault settings are enabled.")
		print("Memory Card           - Enabled")
		print("Content Timer         - Disabled")
		# print("Reset Button Behavior - Go back to main menu")
		print("Autorun Probability   - 5")
		print("Special Argument      - Don't use")
		choice = makeChoice(limitedString("Would you like to enable advanced settings instead of the default? If you do, you will be asked to manually set these options for each new game/movie."), ["Yes", "No"])
		if choice == 1:
			useDefaultSettings = False
			print("Advanced settings enabled.")
			sleep(msgSleep)
	else:
		print("\nAdvanced settings are enabled.")
		print("Memory Card           - Ask for each content")
		print("Content Timer         - Ask for each content")
		# print("Reset Button Behavior - Ask for each content")
		print("Autorun Probability   - Ask for each content")
		print("Special Argument      - Ask for each content")
		choice = makeChoice(limitedString("Would you like to re-enable default settings? If you do, you will no longer be asked to manually set these options."), ["Yes", "No"])
		if choice == 1:
			useDefaultSettings = True
			print("Default settings enabled.")
			sleep(msgSleep)
	inputHidden("Press Enter to continue.")

def initScreen():
	clearScreen()
	print()
	printTitle("Gamecube Demo Disc Tool")
	print()

def printOriginalContents(printHeader=True):
	print("\nCurrent demo disc contents:")
	if len(contentArray) == 0:
		print("None")
	else:
		if printHeader:
			print("TYPE     FOLDER                          FILENAME                        ARGUMENT           MEMCARD   TIMER   ESRB RATING      AUTORUN PROB.")
		for content in contentArray:
			print(shorten(content[0],  7).ljust( 9), end='')
			print(shorten(content[1], 30).ljust(32), end='')
			print(shorten(content[2], 30).ljust(32), end='')
			print(shorten(content[3], 17).ljust(19), end='')
			print(shorten(content[5],  8).ljust(10), end='')
			print(shorten(content[6],  6).ljust( 8), end='')
			print(shorten(content[8], 15).ljust(17), end='')
			print(shorten(content[9],  7).ljust(9))
	print("\nMaximum disc size: "+str(maxSize)+" MB")
	print("Disc space used:   "+str(round(discSize, 3))+" MB")

def printHelpContents():
	initScreen()
	printOriginalContents()
	print("\n")
	print("\n"+limitedString("TYPE          - The type of content (Game or Movie; GBA content counts as a game)", 80, "", "                "))
	print("\n"+limitedString("FOLDER        - The on-disc folder containing textures (logo, etc.) and content-specific configuration", 80, "", "                "))
	print("\n"+limitedString("FILENAME      - The on-disc file containing the actual game/movie", 80, "", "                "))
	print("\n"+limitedString("ARGUMENT      - Special argument for specific content (e.g. the GBA ROM in GBA content); usually NULL", 80, "", "                "))
	print("\n"+limitedString("MEMCARD       - Should the memory card be enabled; usually ON for full games, OFF for everything else", 80, "", "                "))
	print("\n"+limitedString("TIMER         - The amount of time in minutes before the content auto-quits back to the menu; 0 for unlimited or movie", 80, "", "                "))
	print("\n"+limitedString("ESRB RATING   - The ESRB rating", 80, "", "                "))
	print("\n"+limitedString("AUTORUN PROB. - The frequency of this content auto-playing if no buttons are pressed on the menu; 0 (never; recommended for games) through 5 (often; recommended for movies)", 80, "", "                "))
	inputHidden("\nPress Enter to continue.")

def printCredits():
	clearScreen()
	print("\nGamecube Demo Disc Tool")
	print("Made by GateGuy")
	print("https://github.com/GateGuy/GCDemoDiscTool")
	print("\nGC-GBA EmuInjector")
	print("Made by GateGuy")
	print("https://github.com/GateGuy/GC-GBA-EmuInjector")
	print("\nGC-GBA TransferInjector")
	print("Made by GateGuy")
	print("https://github.com/GateGuy/GC-GBA-TransferInjector")
	print("\nGamecube ISO Tool")
	print("Made by FIG2K4")
	print("http://www.wiibackupmanager.co.uk/gcit.html")
	print("\nGCMtoTGC")
	print("Made by Zochwar & Plootid")
	print("https://www.gc-forever.com/forums/viewtopic.php?t=17&start=24")
	print("\nTGCtoGCM")
	print("Made by Zochwar & Plootid")
	print("https://www.gc-forever.com/forums/viewtopic.php?t=17&start=24")
	print("\nWiimms Image Tool")
	print("Made by Wiimm")
	print("https://szs.wiimm.de/wimgt/")
	inputHidden("")

if __name__ == '__main__':
	main()