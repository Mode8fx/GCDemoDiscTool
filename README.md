# GC Demo Disc Tool
This is a Windows utility that allows you to modify, add, or remove contents on an official Gamecube US demo disc. This includes almost all Interactive Multi-Game Demo Discs found at store kiosks, the Preview Disc, the Mario Kart: Double Dash Bonus Disc, and possibly others. The output ISO runs on both a real console and Dolphin.

![](https://github.com/GateGuy/GCDemoDiscTool/blob/main/screenshot.png)

### Features
- Add any Gamecube ISO/GCM file to a demo disc, along with the appropriate menu graphics (icons, etc.)
- Inject a GBA ROM (16 MB or less) into the official GBA emulator found on some demo discs
- Inject a GBA ROM (256 KB or less) into the GBA demo found on the Preview Disc for transfer to a GBA using the link cable
- Optionally set a timer or disable use of the memory card on a per-game basis, like the original kiosks
- Change the disc ID, name, banner, and autoplay timer (amount of time with no button presses before content autoplays)
- User friendliness is prioritized, with conversion and extraction done automatically (command line knowledge isn't required, Gamecube ISOs/GCMs are automatically converted into the appropriate format, PNG files can be used for textures, etc.)

### Legal Disclaimer
No copyrighted content is included with this program. You have to supply the demo disc, ISOs, files for GBA injection, etc.

### Included Programs/Credits
Some of the tools bundled with this program are not made by me, but are required for its use:
- [Gamecube ISO Tool](http://www.wiibackupmanager.co.uk/gcit.html) (Made by FIG2K4)
- [GCMtoTGC](https://www.gc-forever.com/forums/viewtopic.php?t=17&start=24) (Made by Zochwar & Plootid)
- [TGCtoGCM](https://www.gc-forever.com/forums/viewtopic.php?t=17&start=24) (Made by Zochwar & Plootid)
- [Wiimms Image Tool](https://szs.wiimm.de/wimgt/) (Made by Wiimm)

Additionally, the remaining tools are made by me and were (very slightly) modified for use in this program:
- [GC-GBA EmuInjector](https://github.com/GateGuy/GC-GBA-EmuInjector)
- [GC-GBA Transfer Injector](https://github.com/GateGuy/GC-GBA-TransferInjector)

### Known Bugs/Issues
- Because the demo disc uses an internal ID that is different from any of its content, save files will look for this ID; in other words, a save file created for a game will not be compatible with a version of that game that exists on a generated demo disc
- ESRB rating icons (the ones that appear onscreen after selecting a game) may have incorrect sizes
- TPL texture files generated from multiple images take up slightly more space than they should; they are initially converted to the wrong format, and only the first image is changed to what it should be
