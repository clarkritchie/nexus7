# Nexus 7 Bulk Tablet Deployment Script #
-------------

This Python script was developed for use on a project to deploy 1,200 Google Nexus 7 tablets.

*Disclaimer*
-------------
Proceed at your own risk!  I take no responsibility if you brick your own tablet.  That said, I've run this many, many, many times on numerous Nexus 7 tablets, and I have not bricked one tablet.


### Background
Our project had a few specific requirements worth noting, including a) rooting the tablet was not approved, and b) users were not required to have Google accounts to use the tablet.

We received a large shipment of Nexus 7 tablets (2012 Wi-Fi edition, a.k.a. "nakasi") running Android 4.2.  First, we wanted to upgrade them all to run Android 4.4.  Second, we wanted to be able to patch the tablets with what would otherwise be an OTA upgrade (e.g. 4.4.0 to 4.4.2).  Third, we wanted to be able to pre-install a bunch of apps.  Fourth, we wanted the ability to copy a set of files onto the tablet.

Some of of the apps we pre-installed were custom/in-house developed.  Others were free apps available in the Play store.  Because our users were not required to have Google accounts, we found the [APK Extractor](https://play.google.com/store/apps/details?id=net.sylark.apkextractor&hl=en) to be useful to work with this requirement.  On a test tablet, we could login to a Google account, install an app via the Play store, then extract the APK for that app.

At this time, Android does not seem to offer a lot of automation for bulk deployments like ours.  We experimented with things like adb backup/restore in an effort to clone tablets, however ultimatley went with the approach below.

This script can be used 1) to upgrade the Android OS, and 2) install a series apps are available locally on disk as APK files, and 3) copy files onto the tablet.

### Python 3
* This script requires Python 3 (Python 3.3.2 at the time of this writing).  The original version of this script was developed using Python 2.7.5.  We switched to Python's multiprocessing capabilities.  It was developed using Python 3.3.2.  With 5 tablets attached via a USB hub, I was able to flash all 5 to Android 4.3 in approximatley 5:38.  Each additional tablet adds around ~30 seconds.

### Performance
Below are some runtimes I observed upgrading the Android OS (4.2 to 4.3) on 5 tablets connected via a USB hub to a MacBook Pro (2.9 GHz i7):

  * ```./n7p.py completed - 2 tablet(s) in 0:04:00.172587```

  * ```./n7p.py completed - 3 tablet(s) in 0:04:28.856906```

  * ```./n7p.py completed - 4 tablet(s) in 0:05:01.472792```

  * ```./n7p.py completed - 5 tablet(s) in 0:05:38.462541```

### Platform Compatability
This script has been run successfully on Mac computers running OS/X 10.8 and 10.9 and a PC running Windows 7 Starter Edition.

### Setup

1. Install the [Android SDK](http://developer.android.com/sdk/index.html).
2. Update the paths in the .ini file (n7.ini) -- see Edit Config File below.
3. If upgrading the Android OS, download a [Factory image](https://developers.google.com/android/nexus/images) of Android that is appropriate for your tablet
4. Install or confirm you are using Python 3 (e.g.  ```python -V``` or maybe ```python3 -V```) should return something that shows the version of Python you are running)
5. If patching the Android OS, download a .zip file containing the patch -- normally this is available online shortly after an official Android OTA update.
6. Connect any number of tablets to your computer via a USB hub.
7. Windows users will probably need to install USB drivers for the Nexus 7.  These can be downloaded from [Google](http://developer.android.com/sdk/win-usb.html) - see also Windows Driver Note below.

### Edit Config File
Edit the included sample config file (n7.ini) to include:

  * Path to your adb executable
  
  * Path to your fastboot executable
  
  * Path to your copy of the bootloader
  
  * Path to your copy of the Android OS image
  
  * Path to your copy of the Android OS patch file
  
  * Path to your directory of APK files
  
  * Up to 5 files to copy onto the tablet and their target destination (path) on the tablet
  
If no configuration file is specified, the script assumes a file named ```n7.ini``` is in the same directory as the script itself.  An alternate configuration file can be specified using the "-c" parameter, e.g.  ```./n7p.py -c OTHERFILE``` - where OTHERFILE is a file in the same structure as the included n7.ini.

  
### Use Case 1: Update Android OS
1. Update config file, as appropriate.
2. Boot each tablet into the Android bootloader by holding the down volume button and press the power button.
3. Run the script with the "-u" parameter, e.g. ```./n7p.py -u``` 
4. When each tablet is complete, it will reboot into the new version of Android.  Complete the setup wizard.  Note that the final step (e.g. with the ```-w update``` parameters) can take several minutes to copy the update file (several hundred megabytes).  During this time there is not much in the way of visible indicators that something is actually happening on the tablet.

##### Bootloader Note
- The script will unlock the bootloader,de but manual intervention on each tablet is required.  Check for prompts on each tablet's screen -- you will need to press the power button to unlock the bootloader.  The script will then continue.

### Use Case 2: Patch Android OS
1. Update config file, as appropriate.
2. Boot each tablet into the Android recovery mode by holding the down volume button and press the power button, use the volume up/down and choose Recovery mode.  Press the power button to enter recovery mode.  The tablet should restart and end with an Android logo with a exclamation mark.  See also: [Guide: How to Use “adb sideload” to Update a Nexus Without Root or Custom Recovery](http://www.droid-life.com/2013/02/12/guide-how-to-use-adb-sideload-to-update-a-nexus-without-root-or-custom-recovery/)
3. Press Volume Up and Power buttons at the same time to bypass this screen and enter stock recovery.
4. With Volume Down, highlight “apply update from ADB.” Press Power to choose it.
5. Run the script with the "-p" parameter, e.g. ```./n7p.py -p```
6. After the script completes, note that each tablet will verify the integrity of the patch file and then apply the patch, a process that may take several minutes.  When the patch is complete, use the power button to manually choose the option to reboot.
7. Verify Android version in System settings.  Note patching fails if the patch is not for the correct version of Android (e.g. 4.4.2 patch applied to Android 4.3.0).

##### Windows ADB Driver Note
Windows did not recognize my tablet when it was booted into recovery mode -- e.g. three low beeps -- and as a result I could not patch the OS as adb could not see any tablets.  See [Windows doesn't recognize Nexus 7 in recovery mode](http://android.stackexchange.com/questions/57011/windows-doesnt-recognize-nexus-7-in-recovery-mode)).  Koushik Dutta's [Universal ADB Driver for Windows](https://github.com/koush/UniversalAdbDriver) worked great for me on Windows 7.


### Use Case 3: Install Apps
##### Prepare Each Tablet
1. If you flashed the tablet (as above) or just unboxed it, you will need to complete the Android setup wizard.
2. Once your tablet is ready to use, access *Settings* and scroll down to *About tablet* - tap to select.
3. Scroll down to the bottom again to *Build number*, tap this 7 times to enable Developer mode.
4. Return to Settings and choose Developer Options.  Tap to enable USB Debugging.  Press OK to continue.  Press OK to allow connections from your computer.
5. Tap to disable *Verify apps over USB*.  Press the home button to exit Settings.

##### Install Apps
1. Update config file, as appropriate.
2. Once all your tablets are prepped, run the script with no parameters, e.g. ```./n7p.py -a``` 
3. Confirm apps were installed.

##### Windows ADB Driver Note
On my Windows computer, Windows seemed to recognize my device -- e.g. low beep/high beep -- but adb could not see it (e.g. ```adb devices```).  If this happens to you, try rolling the driver back to the version provided by Google (noted above in Setup).

### Use Case 4: Copy Files onto Tablet
1. Update config file, as appropriate.
2. Follow steps under Prepare Each Tablet under Use Case 2: Install Apps
3. Once all your tablets are prepped, run the script with no parameters, e.g. ```./n7p.py -f``` 
4. Confirm files copied to your tablet using a file manager app or ```adb shell```
