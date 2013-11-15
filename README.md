# Nexus 7 Bulk Tablet Deployment Script #
-------------

This Python script was developed for use on a project to deploy over 1,200 Google Nexus 7 tablets.

*Disclaimer*
-------------
Proceed at your own risk!  I take no responsibility if you brick your own tablet.  That said, I've run this many times and have not bricked one tablet.


### Background
Our project had a few specific requirements worth noting, including a) rooting the device was not approved, and b) users were not required to have Google accounts to use the tablet.

We received a large shipment of Nexus 7 tablets running Android 4.2.  First, we wanted to upgrade them all to run Android 4.3.  Second, we wanted to pre-install a series of apps.

Some of of the apps we pre-installed were custom/in-house developed.  Others were free apps available in the Play store.  Because our users were not required to have Google accounts, we found the [APK Extractor](https://play.google.com/store/apps/details?id=net.sylark.apkextractor&hl=en) to be useful to work with this requirement.  On a test tablet, we could login to a Google account, install an app via the Play store, then extract the APK for that app.

At this time, Android does not seem to offer a lot of automation for bulk deployments like ours.  We experimented with things like adb backup/restore in an effort to clone tablets, however ultimatley went with the approach below.

This script can be used 1) to upgrade the Android OS, and 2) to install a series apps are available locally on disk as APK files.

This script can be improved upon.  For example, update argument parsing to use the getopt module, and/or remove the hard coded paths.

### Serial, Parallel Versions
* The version titled **nexus7.py** was my first iteration and developed using Python 2.7.5.  With 5 tablets attached via a USB hub, I was able to flash all 5 to Android 4.3 in approximatley 18 minutes.
* The version titled **nexus7parallel.py** was my second iteration.  This version uses Python's multiprocessing capabilities.  It was developed using Python 3.3.2.  With 5 tablets attached via a USB hub, I was able to flash all 5 to Android 4.3 in approximatley 5:38.  Each additional tablet adds around ~30 seconds.  In fact, here are some runtimes I observed with 5 tablets connected via a USB hub to a MacBook Pro (2.9 GHz i7):

  * ```./nexus7parallel.py completed - 2 tablet(s) in 0:04:00.172587```

  * ```./nexus7parallel.py completed - 3 tablet(s) in 0:04:28.856906```

  * ```./nexus7parallel.py completed - 4 tablet(s) in 0:05:01.472792```

  * ```./nexus7parallel.py completed - 5 tablet(s) in 0:05:38.462541```
* The version titled **nexus7parallel-275.py** is incomplete.  It was my working version of multiprocessing until I decided to switch to Python 3.


### Setup

1. Install the [Android SDK](http://developer.android.com/sdk/index.html).
2. You must update the hardcoded paths in the script as they point to things like the adb and fastboot executables, Android OS image files, and/or a directory of locally hosted APK files.
3. Connect any number of tablets to your computer via a USB hub.

### Use Case 1: Flash Tablets

1. Boot each device into the Android bootloader by holding the down volume button and press the power.
2. Run the script with the "flash" parameter, e.g. ```./nexus7.py flash``` or ```./nexus7parallel.py flash``` 

##### Notes
- The script will unlock the bootloader, but manual intervention on each tablet is required.  Check for prompts on each tablet's screen -- you will need to press the power button to unlock the bootloader.  The script will then continue.

### Use Case 2: Install APK files
##### Prepare Each Tablet
1. If you flashed the device (as above) or just unboxed it, you will need to complete the Android setup wizard.
2. Once your tablet is ready to use, access *Settings* and scroll down to *About tablet* - tap to select.
3. Scroll down to the bottom again to *Build number*, tap this 7 times to enable Deeloper mode.
4. Return to Settings and choose Developer Options.  Tap to enable USB Debugging.  Press OK to continue.  Press OK to allow connections from your computer.
5. Tap to disable *Verify apps over USB*.  Press the home button to exit Settings.

##### Run the APK installer
1. Once all your devices are prepped, run the script with no parameters, e.g. ```./nexus7.py``` or ```./nexus7parallel.py``` 
