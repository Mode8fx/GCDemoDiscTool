import sys
import os
from os import path
import shutil
import getopt
import subprocess
from gatelib import *

currFolder = getCurrFolder()

gcit = path.join(currFolder, "apps", "gcit.exe")
tgctogcm = path.join(currFolder, "apps", "tgctogcm.exe")
wimgt = path.join(currFolder, "apps", "wimgt.exe")

outputFolder = path.join(currFolder, "output")
tempFolder = path.join(currFolder, "temp")
tempGCFolder = path.join(tempFolder, "GC")

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "ha:c:t:", ["help"])
	except getopt.GetoptError:
		printHelp()
		sys.exit(2)
	bgPath = ""
	allOpts = [opt[0] for opt in opts]
	if not ("-a" in allOpts and "-c" in allOpts):
		printHelp()
		sys.exit()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			printHelp()
			sys.exit()
		elif opt == "-a":
			gbaFile = setPathWithArg(arg, "GBA file", [".gba", ".bin"])
			if path.getsize(gbaFile) > 16777216:
				sys.exit("This file is too big. Maximum size for GBA ROM in official emulator is 16 MB.")
		elif opt == "-c":
			gcFile = setPathWithArg(arg, "Gamecube file", [".iso", ".gcm", ".tpl"])
		elif opt == "-t":
			bgPath = setPathWithArg(arg, "Background texture", [".png", ".tpl", ".tex0", ".bti", ".breft"])
	initTempFolder()
	# Convert the Gamecube file from TGC (if necessary)
	print("\nCopying game file to temp folder...")
	oldGame = gcFile
	gcFile = path.join(tempFolder, path.basename(oldGame))
	shutil.copy(oldGame, gcFile)
	if path.splitext(gcFile)[1] == ".tgc":
		subprocess.call('\"'+tgctogcm+'\" \"'+gcFile+'\" \"'+path.splitext(gcFile)[0]+".gcm"+'\"')
		os.remove(gcFile)
		gcFile = path.splitext(gcFile)[0]+".gcm"
	# Extract the Gamecube file
	subprocess.call('\"'+gcit+'\" \"'+gcFile+'\" -q -f gcreex -d \"'+tempGCFolder+'\"')
	gcFolder = path.join(tempGCFolder, listdir(tempGCFolder)[0])
	# Copy over the GBA ROM
	gbaRomPath = path.join(gcFolder, "root", "bin", "kiosk031204MDK.bin")
	if not path.exists(gbaRomPath):
		gbaRomPath = path.join(gcFolder, "root", "bin", "MarioPinballLand_DEMO.bin")
	try:
		os.remove(gbaRomPath)
	except:
		sys.exit("Invalid Gamecube file.")
	shutil.copy(gbaFile, gbaRomPath)
	# Copy over the defined TPLs
	if bgPath != "":
		os.remove(path.join(gcFolder, "root", "F_02.tpl"))
		subprocess.call('\"'+wimgt+'\" ENCODE \"'+bgPath+'\" -d \"'+path.join(gcFolder, "root", "F_02.tpl")+'\" -x TPL')
	# Build the new ISO
	createDir(outputFolder)
	while len(listdir(outputFolder)) > 0:
		input("\nA file already exists in "+outputFolder+". Please move, rename, or delete this file.\nPress Enter to continue.")
	subprocess.call('\"'+gcit+'\" \"'+gcFolder+'\" -q -d \"'+path.join(outputFolder, "output.iso")) # the name doesn't matter; gcit.exe forces a name
	input("\nCreated new ISO in "+outputFolder+".\nPress Enter to exit.")
	sys.exit()


def setPathWithArg(arg, fileTypeName, formats=[]):
	file = path.join(currFolder, arg)
	if not path.isfile(file):
		file = arg
	if not path.isfile(file):
		sys.exit("Error: "+fileTypeName+" not found.")
	if len(formats) > 0:
		if not path.splitext(file)[1] in formats:
			s = formats[0]
			for f in formats[1:]:
				s += ", "+f
			sys.exit("Error: "+fileTypeName+" must be one of the following formats: "+s)
	return file

def initTempFolder():
	if path.isdir(tempFolder):
		shutil.rmtree(tempFolder)
	createDir(tempFolder)
	mkdir(tempGCFolder)

def printHelp():
	print("\nUsage: GCGBA_ei.exe -a <input GBA> -c <input GC> -t <TPL/PNG>")
	print()
	print("-a <the GBA ROM that will be injected>")
	print("-c <the Gamecube file that the GBA ROM will be injected into; this is zz_MarioVSDonkey_game.tgc, which can be extracted from Interactive Multi-Game Demo Disc Version 16/17, or zz_MarioPinballLand_game.tgc, which can be extracted from Interactive Multi-Game Demo Disc Version 18>")
	print("-t <optional; a new texture/PNG file for the background image; if not set, the exiting background will be used>")
	print()
	print("Use the provided template_F_02.png as a template for a custom background image.")

if __name__ == '__main__':
	main(sys.argv[1:])