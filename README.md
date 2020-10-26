# GC Demo Disc Tool
This is a Windows utility that allows you to modify, add, or remove contents on an official Gamecube US demo disc. This includes almost all Interactive Multi-Game Demo Discs found at store kiosks, the Preview Disc, the Mario Kart: Double Dash Bonus Disc, and possibly others. The output ISO runs on both a real console and Dolphin.

### Features
- Add any Gamecube ISO/GCM file to a demo disc, along with the appropriate menu graphics (icons, etc)
- Inject a GBA ROM (16 MB or less) into the official GBA emulator found on some demo discs
- Inject a GBA ROM (256 KB or less) into the GBA demo found on the Preview Disc for transfer to a GBA using the link cable
- Optionally set a timer or disable use of the memory card on a per-game basis, like the original kiosks
- Change the disc ID, name, banner, and autoplay timer (amount of time with no button presses before content autoplays)
- User friendliness is prioritized, with conversion and extraction done automatically (command line knowledge isn't required, Gamecube ISOs/GCMs are automatically converted into the appropriate format, PNG files can be used for textures, etc.)

### Legal Disclaimer
No copyrighted content is included with this program. You have to supply the demo disc, ISOs, files for GBA injection, etc.

### Included Programs/Credits
Some of the tools bundled with this program are not made by me, but are required for its use:
- [Gamecube ISO Tool](http://www.wiibackupmanager.co.uk/gcit.html)
- [GCMtoTGC](https://www.gc-forever.com/forums/viewtopic.php?t=17&start=24)
- [TGCtoGCM](https://www.gc-forever.com/forums/viewtopic.php?t=17&start=24)
- [Wiimms Image Tool](https://szs.wiimm.de/wimgt/)
Additionally, the remaining tools are made by me and were (very slightly) modified for use in this program:
- GC-GBA EmuInjector
- GC-GBA Transfer Injector
