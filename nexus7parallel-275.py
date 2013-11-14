#!/Library/Frameworks/Python.framework/Versions/3.3/bin/python3.3

#!/usr/bin/env python
#
# A simple script to:
#  - Install a directory worth of APKs onto N-attached Android devices via USB
#  - Flash N-attached Android devices via USB with unlocked bootloader
#
# Usage:  nexus7parallel.py -- Will install all APKs in the directory path hard coded below
#         nexus7parallel.py flash -- Will flash using the bootloader and Android OS image hard coded below
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
# @see http://stackoverflow.com/questions/7207309/python-how-can-i-run-python-functions-in-parallel
# from multiprocessing import Process
from multiprocessing import Pool

# BEGIN Paths to update:
# path to adb executable
adb='/usr/local/bin/android-sdk/sdk/platform-tools/adb'
# path to fastboot executable
fastboot='/usr/local/bin/android-sdk/sdk/platform-tools/fastboot'
# path to directory of APK files to install
apk_files='/tmp/nexus7/APKs'
# path to the Android OS image file and bootloader
android_image='/tmp/nexus7/image-nakasi-jwr66y.zip'
bootloader='/tmp/nexus7/bootloader-grouper-4.23.img'
# END Paths to update:

def flashTablet( device_id, fastboot, bootloader, android_image ):
    print "Begin flash of tablet %s", device_id
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
        p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line
        retval = p.wait()
        # time.sleep(5)
        print 'End flash of tablet %s', device_id

def installAPKs( device_id, apks, apk_files ):
    print 'Begin APK install on tablet %s', device_id
    # print "Working in Process #%d" % (os.getpid())
    
    for apk in apks:
        print 'Installing %s onto %s', (apk, device_id )
        # ignore Mac .DS_Store and any other hidden files
        if not f.startswith('.'):
            # maybe have to change this from / to \ for Windows?
            cmd = adb + ' -s %s install -r %s/%s' % ( device_id, apk_files, apk )
            print cmd
            # w = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
            w = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            output, errors = w.communicate()
            # w.wait()
            # the re here is only make adb's output a bit more concise
            print "STDOUT: %s" % re.sub("[\t\s\s+]" , " ", output)
            print "STDERR: %s" % re.sub("[\t\s\s+]" , " ", errors)
            # print "   RET: %s" % w.returncode
            #for line in w.stdout.readlines():
            #    print line
            #retval = w.wait()
            #print "Retval = %s" % retval
    # print w.returncode 
    # print 'End APK install on tablet %s' % device_id
    # return 0

    
if __name__ == '__main__':
    
    start_time = time.time()
    
    # if the argument is "flash" then flash the device
    flash=False
    # print "First argument: %s" % str(sys.argv[1])
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
    
    # setup the pool
    # processes = []
    pool = Pool(processes=len(devices)) # argument is number of processes, default is the number of CPUs
    # pool = mp.Pool() # argument is number of processes, default is the number of CPUs
    
    for device_id in devices:
        if device_id is not None:
            print "Using tablet %s", device_id
            if flash:
                print "flash"
                #p = mp.Process( target=flashTablet, args=( device_id, fastboot, bootloader, android_image ))
                #processes.append( p )
                #p.start()
            else:
                # p = mp.Process( target=installAPKs, args=( device_id, apks, apk_files ))
                # processes.append( p )
                # p.start()
                pool.apply_async( installAPKs, args = ( device_id, apks, apk_files, ))
                #pool.map_async(installAPKs, [device_id, apks, apk_files])
    pool.close()
    pool.join()
    # wait for all worker processes to finish
    # print "Processes = %s" % len(processes)
    #for r in processes:
    #    r.join()
        
    elapsed_time = time.time() - start_time
    
    print '\n\n%s completed - %s tablet(s) in %.03f seconds\n\n',( sys.argv[0], len(devices), elapsed_time )  