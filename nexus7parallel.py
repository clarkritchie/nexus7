#!/usr/bin/python
#
# A simple script to:
#  - Install a directory worth of APKs onto N-attached Android devices via USB
#  - Flash N-attached Android devices via USB with unlocked bootloader
#
# Usage:  primr.py -- Will install all APKs in the directory path hard coded below
#         primr.py flash -- Will flash using the bootloader and Android OS image hard coded below
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import subprocess, sys, re, time
from os import listdir
from os.path import isfile, join
# http://stackoverflow.com/questions/7207309/python-how-can-i-run-python-functions-in-parallel
from multiprocessing import Process

# Paths to update:
# path to adb executable
adb='/Users/clarkritchie/android-sdk/sdk/platform-tools/adb'
# path to fastboot executable
fastboot='/Users/clarkritchie/android-sdk/sdk/platform-tools/fastboot'
# path to directory of APK files to install
apk_files='/Users/clarkritchie/Dropbox/Work/Inveneo/PRIMR/APKs'
# path to the Android OS image file
android_image='/Users/clarkritchie/Dropbox/Work/Inveneo/PRIMR/firmware/nakasi-jwr66y-diffbootload/image-nakasi-jwr66y.zip'
bootloader='/Users/clarkritchie/Dropbox/Work/Inveneo/PRIMR/firmware/nakasi-jwr66y-diffbootload/bootloader-grouper-4.23.img'

def flashTablet( device_id, fastboot, bootloader, android_image ):
    print 'Beginning flash tablet of %s' % device_id
    # for i in xrange(10000000): pass
    flash_cmds = [
        '%s -s %s oem unlock' % ( fastboot, device_id ),
        '%s -s %s erase boot' % ( fastboot, device_id ),
        '%s -s %s erase cache' % ( fastboot, device_id ),
        '%s -s %s erase recovery' % ( fastboot, device_id ),
        '%s -s %s erase system' % ( fastboot, device_id ),
        '%s -s %s erase userdata' % ( fastboot, device_id ),
        '%s -s %s flash bootloader %s' % ( fastboot, device_id, bootloader ),
        '%s -s %s reboot-bootloader' % ( fastboot, device_id ),
        'sleep 10',
        '%s -s %s -w update %s' % ( fastboot, device_id, android_image ),
    ]
    for cmd in flash_cmds:
        print cmd
        time.sleep(0.1)
    print 'End flash tablet of %s' % device_id

def installAPKs( device_id, apks ):
    print 'Beginning APK install on tablet of %s' % device_id
    # for i in xrange(10000000): pass
    
    for apk in apks:
        print apk
        time.sleep(0.1)
        print 'Installing %s onto %s' % ( apk, device_id )
        # ignore Mac .DS_Store and any other hidden files
        if not f.startswith('.'):
            # maybe have to change this from / to \ for Windows?
            cmd=adb + ' -s %s install -r %s/%s' % (device_id,apk_files,apk)
            p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                print line
            retval = p.wait()
    print 'End APK install on tablet of %s' % device_id

    
if __name__ == '__main__':
    
    # if the argument is "flash" then flash the device
    flash=False
    # print ("First argument: %s" % str(sys.argv[1]))
    if len(sys.argv) > 1:
        # Get the arguments list 
        cmdargs = str(sys.argv)
        if str(sys.argv[1]) == 'flash':
            flash=True
    
    if flash:
        print "Flash attached tablets"
        cmd=fastboot + " devices"
    else:
        print "Install APKs on attached tablets"
        cmd=adb + " devices"
    
    # get all the APKs into a list
    apks = [ f for f in listdir(apk_files) if isfile(join(apk_files,f)) ]
    
    # get a list of device IDs for all attached tablets
    devices = []
    p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        # print line
        # device_id = re.match( '^([%&+ \w]+).*device$', line )
        device_id = re.match( '^([%&+ \w]+).*[a-z]+$', line )
        # for each device, install the APKs one by one
        if device_id is not None:
            devices.append(device_id.group(1))
    retval = p.wait()
    
    devices = [ 10,4 ]
    
    for device_id in devices:
        if device_id is not None:
            print "Using Device ", device_id
            
            if flash:
                print "y"
                #p1 = Process(target=flashTablet, args=( device_id, fastboot, bootloader, android_image ))
                #p1.start()
                # p1.join()
            else:
                print "x"
                p1 = Process(target=installAPKs, args=( device_id, apks, apk_files ))
                p1.start()
                
