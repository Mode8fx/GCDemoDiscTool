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
useDefaultSettings = True

inputSleep = 0.5
msgSleep = 1

def main():
	global discSize

	Tk().withdraw()
	initTempFolder()
	manageDemoDisc()
	discSize = getDirSize(demoDiscFolder)/1024.0/1024
	while True:
		clearScreen()
		setOriginalContents()
		printOriginalContents()
		choice = makeChoice("What would you like to do?", ["Add content to disc", "Remove content from disc", "Build disc", "Change disc settings", ("Enable" if useDefaultSettings else "Disable")+" advanced settings", "Help (Contents)", "Quit"])
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
	sleep(msgSleep)
	sourceDemoDisc = askopenfilename(filetypes=[("Gamecube Demo Discs", ".iso .gcm")])
	if sourceDemoDisc == "":
		print("Demo disc not found.")
		sys.exit()
	subprocess.call('\"'+gcit+'\" \"'+sourceDemoDisc+'\" -q -f gcreex -d \"'+tempDemoDiscFolder+'\"')
	demoDiscFolder = path.join(tempDemoDiscFolder, listdir(tempDemoDiscFolder)[0])
	contentsFile = path.join(demoDiscFolder, "root", "config_e", "contents.txt")
	integrateExe = path.join(demoDiscFolder, "root", "config_e", "integrate.exe")
	integratedFile = path.join(demoDiscFolder, "root", "integrated.txt")
	if path.isfile(integrateExe):
		print("\nValid demo disc.")
		sleep(msgSleep)
	else:
		print("\nInvalid disc. Quitting.")
		sleep(msgSleep)
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

	choice = makeChoice("Which type of content would you like to add?",
		["Gamecube ISO/GCM/TGC File", "GBA ROM (for use in official emulator)", "GBA ROM (for transfer to GBA)", "N64 ROM (for use in official emulator)", "Go Back"])
	if choice == 1:
		print("\nPlease select a Gamecube ISO/GCM/TGC File.")
		sleep(msgSleep)
		newGCGame = askopenfilename(filetypes=[("Gamecube Game File", ".iso .gcm .tgc")])
		if newGCGame == "":
			print("\nAction cancelled.")
			sleep(msgSleep)
		else:
			print("Done.")
			sleep(msgSleep)
			newLogo, newLogo2, newManual, newScreen = askForTextures(True)
			memcard, timer, forcereset, rating, autorunProb, argument = askForSettings(True)
			addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, forcereset, rating, autorunProb)
	elif choice == 2:
		if path.exists(gbaEmulatorFile1):
			gbaEmulatorFile = gbaEmulatorFile1
		elif path.exists(gbaEmulatorFile2):
			gbaEmulatorFile = gbaEmulatorFile2
		else:
			print("\nGBA emulator file not found. For more information, read '/apps/PUT MvDK OR MPL DEMO HERE.txt'")
			sleep(inputSleep)
			inputHidden("Action cancelled. Press Enter to continue.")
		print("\nPlease select a GBA ROM File.")
		sleep(msgSleep)
		newGBAGame = askopenfilename(filetypes=[("GBA ROM File", ".gba .bin")])
		if newGBAGame == "":
			print("\nAction cancelled.")
			sleep(msgSleep)
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
				f_02 = ""
				choice = makeChoice("Would you like to add a custom overlay to the GBA emulator app or use the existing overlay?", ["Add new overlay", "Keep current overlay"])
				if choice == 1:
					f_02 = askForFile("Select the Overlay. This is the image/texture file of the overlay surrounding the game.\nIf you do not select a texture, the current texture will be used.\n(Recommended size: at least 608x448)",
						[("Texture File", ".png .tpl .tex0 .bti .breft")], "", "Skipped Overlay.")
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, argument, memcard, timer, forcereset, rating, autorunProb, isEmulatedGBA=True, gbaOverlay=f_02)
	elif choice == 3:
		if not path.exists(gbaTransferFile):
			print("\nGBA transfer file not found. For more information, read '/apps/PUT wario_agb.tgc HERE.txt'")
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
				sleep(msgSleep)
			else:
				print("Done.")
				sleep(msgSleep)
				newLogo, newLogo2, newManual, newScreen = askForTextures(True)
				memcard, timer, forcereset, rating, autorunProb, _ = askForSettings(False)
				err, load, ind, done = askForGBATransferTextures()
				addNewContent("<GAME>", newGCGame, newLogo, newLogo2, newManual, newScreen, "file://"+path.basename(newGCGame), memcard, timer, forcereset, rating, autorunProb, gbaErr=err, gbaLoad=load, gbaInd=ind, gbaDone=done)
	elif choice == 4:
		print("\nTo inject an N64 ROM, use the GCM N64 ROMS Injector.")
		print("https://github.com/sizious/gcm-n64-roms-injector")
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
	# else, do nothing (go back to menu)

def removeContent():
	if len(contentArray) == 0:
		print("\nThere is no content to remove.")
		sleep(msgSleep)
		return
	choice = makeChoice("What would you like to remove?", [c[0]+" | "+c[1]+" | "+c[2] for c in contentArray]+["Go Back"])
	if choice == len(contentArray):
		print("\nAction cancelled.")
		sleep(msgSleep)
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
	sleep(msgSleep)

def buildDisc():
	global contentArray

	if discSize > 1375.875:
		print("\nThe contents of the extracted disc take up too much space.")
		print("If you created a screen.tpl with more than one image, and you are only a few MB over the allocated space, you may want to manually open the TPL with a program like BrawlBox and change the format of each texture to CMPR (the default is RGB5A3, which takes up more space).")
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
		return
	if len(contentArray) == 0:
		print("\nYou must add at least one game/movie to the disc before building.")
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
		return
	if len(contentArray) < 5:
		choice = makeChoice("You have fewer than 5 games/movies. To prevent unintended visual bugs, would you like to duplicate menu options? This will not take up any additional space.", ["Yes (Recommended)", "No"])
		if choice == 1:
			originalContentArray = copy(contentArray)
			while len(contentArray) < 5:
				contentArray += originalContentArray
			integrateFromContentArray()
	askForIDAndName()
	# Finalize
	print("\nThis will build the contents of the extracted disc into a new ISO.")
	print("If you would like to manually change any contents (for example, the order of content on the menu in \"/temp/DemoDiscGcReEx/YOURDEMODISC/root/config_e/contents.txt\"), do so now.")
	choice = makeChoice("Continue?", ["Yes", "No, go back", "Quit"])
	if choice == 2:
		return
	if choice == 3:
		sys.exit()
	createDir(outputFolder)
	while len(listdir(outputFolder)) > 0:
		print("A file already exists in "+outputFolder+". Please move, rename, or delete this file.")
		sleep(inputSleep)
		inputHidden("Press Enter to continue.")
	subprocess.call('\"'+gcit+'\" \"'+demoDiscFolder+'\" -q -d \"'+path.join(outputFolder, "output.iso")) # the name doesn't matter; gcit.exe forces a name
	print("\nCreated new ISO in "+outputFolder+".")
	sleep(inputSleep)
	inputHidden("Press Enter to exit.")
	sys.exit()

def askForTextures(isGame=True):
	newLogo1 = askForFile("Select Logo 1. This is the menu icon when the content is not highlighted.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: at least 267x89)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_logo.png"), "Skipped Logo 1.")
	newLogo2 = askForFile("Select Logo 2. This is the menu icon when the content is highlighted.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: at least 267x89)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_logo2.png"), "Skipped Logo 2.")
	newManual = askForFile("Select Manual. This is the image/texture file of the controls screen, displayed after selecting a game.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: at least 640x480)",
		[("Texture File", ".png .tpl .tex0 .bti .breft")], path.join(defaultFolder, "template_manual.png"), "Skipped Manual.")

	print("\nSelect Screen. This is the texture file containing up to four image(s) shown on the menu.\nIf you do not select a texture, a default single-color texture will be used.\n(Recommended size: at least 340x270 for earlier discs (they show the screenshot in a smaller window), or at least 640x480 for most discs (the entire background changes depending on the game))")
	sleep(msgSleep)
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
		timer = int(makeChoiceNumInput("What should the time limit be (in minutes)? 0 = unlimited or video", 0, 999))
		forcereset = "ON" if makeChoice("What should the reset button do?", ["Reset current game/movie", "Go back to main menu"]) == 1 else "OFF"
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
	return memcard, timer, forcereset, rating, autorunProb, argument

def askForFile(description, fTypes, defaultFile, skipText):
	print("\n"+description)
	sleep(msgSleep)
	file = askopenfilename(filetypes=fTypes)
	if file == "":
		file = defaultFile
	if path.isfile(file):
		print("Done.")
	else:
		if file != "":
			print("\""+file+"\" not found.")
		print(skipText)
	sleep(msgSleep)
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
			shutil.copy(screen[0], path.join(tempTPLFolder, "image.png"))
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
	sleep(inputSleep)
	inputHidden("Press Enter to continue.")

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
	choice = makeChoice("Would you like to change the ID/Name? Having a unique ID/Name is important for certain ISO loaders.", ["Yes", "No"])
	if choice == 1:
		print("Input the new ID and press Enter. If you do not want to change the ID, press Enter without typing anything else.")
		print("It is strongly recommended that the ID is six characters long and follows this naming convention: (letter)(letter)(letter)(region letter)(number)(number), where (region number) is E (USA), P (PAL), or J (Japan) depending on the region. Example: SNQE12")
		new = input().strip()
		if new != "":
			bootFile.seek(0x0)
			bootFile.write(bytes(new, 'utf-8'))
			for _ in range(6-len(new)):
				bootFile.write(bytes([0x00]))
		print("Input the new name and press Enter. If you do not want to change the ID, press Enter without typing anything else.")
		print("The name should be a maximum of 63 characters long. Anything more will be ignored.")
		new = input().strip()
		if new != "":
			bootFile.seek(0x20)
			bootFile.write(bytes(new[:min(len(new), 63)], 'utf-8'))
			for _ in range(63-len(new)):
				bootFile.write(bytes([0x00]))
		print("ID and Name changed to the following:")
		bootFile.seek(0x0)
		print("ID: "+bootFile.read(6).decode('utf-8'))
		bootFile.seek(0x20)
		print("Name: "+bootFile.read(63).decode('utf-8'))
	bootFile.close()

def changeDiscSettings():
	choice = makeChoice("Which setting would you like to change?",
		["Timer (the amount of time before a random game/movie autoplays; default = 15 seconds)", "Banner (the disc banner that appears in the system menu)" "Go Back"])
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
		choice = makeChoice("Would you like to replace the current banner? You must provide a banner that is already in a .bnr format.", ["Yes", "No"])
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

def changeDefaultContentSettings():
	global useDefaultSettings

	if useDefaultSettings:
		print("Default settings are enabled.")
		print("Memory Card           - Enabled")
		print("Content Timer         - Disabled")
		print("Reset Button Behavior - Go back to main menu")
		print("Autorun Probability   - 5")
		print("Special Argument      - Don't use")
		choice = makeChoice("Would you like to enable advanced settings instead of the default? If you do, you will be asked to manually set these options for each new game/video.", ["Yes", "No"])
		if choice == 1:
			useDefaultSettings = False
			print("Advanced settings enabled.")
			sleep(msgSleep)
	else:
		print("Advanced settings are enabled.")
		print("Memory Card           - Ask for each content")
		print("Content Timer         - Ask for each content")
		print("Reset Button Behavior - Ask for each content")
		print("Autorun Probability   - Ask for each content")
		print("Special Argument      - Ask for each content")
		choice = makeChoice("Would you like to re-enable default settings? If you do, you will no longer be asked to manually set these options.", ["Yes", "No"])
		if choice == 1:
			useDefaultSettings = True
			print("Default settings enabled.")
			sleep(msgSleep)

def printOriginalContents(printHeader=True):
	print("\nCurrent demo disc contents:")
	if len(contentArray) == 0:
		print("None")
	else:
		if printHeader:
			print("TYPE    FOLDER                        FILENAME                      ARGUMENT                      MEMCARD   TIMER   ESRB RATING      AUTORUN PROB.")
		for content in contentArray:
			print(content[0].ljust(8)+content[1].ljust(30)+content[2].ljust(30)+content[3].ljust(30)+content[5].ljust(10)+content[6].ljust(8)+content[8].ljust(17)+content[9])
	print("\nMaximum disc size: 1375.875 MB")
	print("Disc space used:   "+str(round(discSize, 3))+" MB")

def printHelpContents():
	clearScreen()
	printOriginalContents()
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