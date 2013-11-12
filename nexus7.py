#!/usr/bin/python
#
# A simple script to:
#  - Install a directory worth of APKs onto N-attached Android devices via USB
#  - Flash N-attached Android devices via USB with unlocked bootloader
#
# Usage:  nexus7.py -- Will install all APKs in the directory path hard coded below
#         nexus7.py flash -- Will flash using the bootloader and Android OS image hard coded below
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

import subprocess, sys, re

from os import listdir
from os.path import isfile, join

# Paths to update:
# path to adb executable
adb='/path/to/android-sdk/sdk/platform-tools/adb'
# path to fastboot executable
fastboot='/path/to/android-sdk/sdk/platform-tools/fastboot'
# path to directory of APK files to install
apk_files='/path/to/APKs'
# path to the Android OS image file
android_image='/path/to/firmware/nakasi-jwr66y-diffbootload/image-nakasi-jwr66y.zip'
bootloader='/path/to/firmware/nakasi-jwr66y-diffbootload/bootloader-grouper-4.23.img'


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

# now install APKs for each attached device
for device_id in devices:
    if device_id is not None:
        print "Using Device ", device_id
        
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
        
        if flash:
            print "Attempting to flash"
            for cmd in flash_cmds:
                print cmd
                p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print line
                retval = p.wait()
        else:
            print "Attempting to install APKs"
            # install APKs
            for f in apks:
                # ignore Mac .DS_Store and any other hidden files
                if not f.startswith('.'):
                    # maybe have to change this from / to \ for Windows?
                    cmd=adb + ' -s %s install -r %s/%s' % (device_id,apk_files,f)
                    p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    for line in p.stdout.readlines():
                        print line
                    retval = p.wait()
                

