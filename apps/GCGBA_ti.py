import sys
import os
from os import path
import shutil
import getopt
import subprocess
from gatelib import *

currFolder = getCurrFolder()

gcit = path.join(currFolder, "gcit.exe")
tgctogcm = path.join(currFolder, "tgctogcm.exe")
wimgt = path.join(currFolder, "wimgt.exe")

outputFolder = path.join(currFolder, "output")
tempFolder = path.join(currFolder, "temp")
tempGCFolder = path.join(tempFolder, "GC")

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "ha:c:", ["help", "err=", "load=", "ind=", "done="])
	except getopt.GetoptError:
		printHelp()
		sys.exit(2)
	errPath = ""
	loadPath = ""
	indPath = ""
	donePath = ""
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
			if path.getsize(gbaFile) > 262144:
				sys.exit("Error: GBA file is too big. Maximum size for GBA transfer is 256 KB.")
		elif opt == "-c":
			gcFile = setPathWithArg(arg, "Gamecube file", [".iso", ".gcm", ".tpl"])
		elif opt == "--err":
			errPath = setPathWithArg(arg, "'err' file", [".png", ".tpl", ".tex0", ".bti", ".breft"])
		elif opt == "--load":
			loadPath = setPathWithArg(arg, "'load' file", [".png", ".tpl", ".tex0", ".bti", ".breft"])
		elif opt == "--ind":
			indPath = setPathWithArg(arg, "'ind' file", [".png", ".tpl", ".tex0", ".bti", ".breft"])
		elif opt == "--done":
			donePath = setPathWithArg(arg, "'done' file", [".png", ".tpl", ".tex0", ".bti", ".breft"])
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
	os.remove(path.join(gcFolder, "root", "agb_wario.bin"))
	shutil.copy(gbaFile, path.join(gcFolder, "root", "agb_wario.bin"))
	# Copy over the defined TPLs
	if errPath != "":
		os.remove(path.join(gcFolder, "root", "err_message.tpl"))
		subprocess.call('\"'+wimgt+'\" ENCODE \"'+errPath+'\" -d \"'+path.join(gcFolder, "root", "err_message.tpl")+'\" -x CMPR')
	if loadPath != "":
		os.remove(path.join(gcFolder, "root", "ing_message.tpl"))
		subprocess.call('\"'+wimgt+'\" ENCODE \"'+loadPath+'\" -d \"'+path.join(gcFolder, "root", "ing_message.tpl")+'\" -x CMPR')
	if indPath != "":
		os.remove(path.join(gcFolder, "root", "indicator.tpl"))
		subprocess.call('\"'+wimgt+'\" ENCODE \"'+indPath+'\" -d \"'+path.join(gcFolder, "root", "indicator.tpl")+'\" -x CMPR')
	if donePath != "":
		os.remove(path.join(gcFolder, "root", "done_message.tpl"))
		subprocess.call('\"'+wimgt+'\" ENCODE \"'+donePath+'\" -d \"'+path.join(gcFolder, "root", "done_message.tpl")+'\" -x CMPR')
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
	print("\nUsage: GCGBA_ti.exe -a <input GBA> -c <input GC> --err <TPL> --load <TPL> --ind <TPL> --done <TPL>")
	print()
	print("-a <the GBA ROM that will be injected>")
	print("-c <the Gamecube file that the GBA ROM will be injected into; this is wario_agb.tgc, which can be extracted from the Nintendo Gamecube Preview Disc>")
	print("--err  <optional; a new texture/PNG file that displays when the transfer from Gamecube to GBA has not started>")
	print("--load <optional; a new texture/PNG file that displays when the transfer is in progress>")
	print("--ind  <optional; a new texture/PNG file that represents the progress bar for the transfer (such as a dot or a pill)>")
	print("--done <optional; a new texture/PNG file that displays when the transfer is complete>")
	print()
	print("All textures have a recommended size of 640x480 except indicator, which is 30x28")

if __name__ == '__main__':
	main(sys.argv[1:])