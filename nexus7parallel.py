#!/usr/local/bin/python3

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

import subprocess, sys, re, time, glob, datetime ,os
# @see http://stackoverflow.com/questions/7207309/python-how-can-i-run-python-functions-in-parallel
# from multiprocessing import Process
from multiprocessing import Pool

# check if we're on a posix or Windows machine
posix = 1
if ( os.name == "nt"): # not sure what other versions of Windows report here
    posix = 0

# BEGIN Paths to update
if ( posix ):
    # path to adb and fastboot executables
    adb='/usr/local/bin/android-sdk/sdk/platform-tools/adb'
    fastboot='/usr/local/bin/android-sdk/sdk/platform-tools/fastboot'
    # path to directory of APK files to install
    apk_files='/tmp/nexus7/APKs'
    # path to the Android OS image file and bootloader
    android_image='/tmp/nexus7/image-nakasi-krt16s.zip' # Android 4.4
    bootloader='/tmp/nexus7/bootloader-grouper-4.23.img'
    
    # test Mac
    android_image='/Users/default/Documents/tablets/android4_4/nakasi-krt16s/image-nakasi-krt16s.zip' # Android 4.4
    bootloader='/Users/default/Documents/tablets/android4_4/nakasi-krt16s/bootloader-grouper-4.23.img'
    apk_files='/Users/default/Documents/tablets/APKs'
    adb='/Users/default/Documents/tablets/android/sdk/platform-tools/adb'
    fastboot='/Users/default/Documents/tablets/android/sdk/platform-tools/fastboot'

else:
    # path to adb and fastboot executables
    adb='c:\\Users\\Heather\\Desktop\\android\\sdk\\platform-tools\\adb'
    fastboot='c:\\Users\\Heather\\Desktop\\android\\sdk\\platform-tools\\fastboot'
    # path to directory of APK files to install
    apk_files='c:\\Users\\Heather\\Desktop\\nexus7'
    # path to the Android OS image file and bootloader
    android_image='c:\\Users\\Heather\\Desktop\\nexus7\\image-nakasi-krt16s.zip' # Android 4.4
    bootloader='c:\\Users\\Heather\\Desktop\\nexus7\\bootloader-grouper-4.23.img'
# END Paths to update

# ******************************************************************************
# flashTablet
# This function will 
# ******************************************************************************
def flashTablet( device_id, fastboot, bootloader, android_image ):
    r = 0
    sleep = 10
    print("Begin flash of tablet %s" % device_id)
    
    flash_cmds = [
        [fastboot,"-s",device_id,"oem","unlock"], # step 0
        [fastboot,"-s",device_id,"erase","boot"], # step 1
        [fastboot,"-s",device_id,"erase","cache"], # step 2
        [fastboot,"-s",device_id,"erase","recovery"], # step 3
        [fastboot,"-s",device_id,"erase","system"], # step 4
        [fastboot,"-s",device_id,"erase","userdata"], # step 5
        [fastboot,"-s",device_id,"flash","bootloader",bootloader], # step 6        
        [fastboot,"-s",device_id,"reboot-bootloader"], # step 7
        # sleep on step 8
        [fastboot,"-s",device_id,"-w","update",android_image] # step 9
    ]
    
    n = 0
    for cmd in flash_cmds:
        # sleep for 10 sec while the bootloader reboots
        if n == 8:
            print ( "Sleeping for %s...\r\n" % sleep )
            time.sleep(sleep)
            
        print('%s: %s' % ( n, cmd ))
        time.sleep(1)
        # bufsize=4096, 
        subp = subprocess.Popen( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr = subp.communicate()
        subp.wait()
        print(stdout.decode())
        print(stderr.decode())
        n += 1
        # time.sleep(5)
    print ('End flash of tablet %s' % device_id)
    return r

# ******************************************************************************
# installAPKs
# This function will install all APK files in a given directory onto all
# connected tablets
# ******************************************************************************
def installAPKs( device_id, apks ):
    r = 0
    print ( 'Begin APK install on tablet %s' % device_id )
    for f in apks:
        print( 'Installing %s onto %s' % ( f, device_id ))
        cmd=adb + ' -s '+device_id+" install -r "+f
        print(cmd)
        subp = subprocess.Popen( [adb,"-s",device_id,"install","-r",f], bufsize=4096, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        # subp = subprocess.Popen( [adb,"-s",device_id,"install","-r",f] )
        # subp = subprocess.Popen( [adb,"-s",device_id,"install","-r",f], bufsize=4096 )
        subp.communicate()
        r = subp.returncode
        subp.wait()
    print( "End APK install on tablet %s" % device_id )
    return r

# for testing subprocess exit problems on Windows 7
def installAPKs_wrapped( device_id, apks ):
    try:
        installAPKs( device_id, apks )
    except:
        print('%s' % (traceback.format_exc()))

def checkReturnCode(r):
    print("Return code: %s" % r)
    
# ******************************************************************************
# Main
# ******************************************************************************
if __name__ == '__main__':
    
    start_time = time.time()
    
    # if the argument is "flash" then flash the device
    flash=False
    # print ("First argument: %s" % str(sys.argv[1]))
    if len(sys.argv) > 1:
        # Get the arguments list 
        cmdargs = str(sys.argv)
        if str(sys.argv[1]) == 'flash':
            flash=True
    
    if flash:
        print ("Flash attached tablets")
        cmd=fastboot + " devices"
    else:
        print ("Install APKs on attached tablets")
        cmd=adb + " devices"
    
    # get all the APKs into a list
    # apks = [ f for f in listdir(apk_files) if isfile(join(apk_files,f)) ]
    apks = glob.glob( apk_files+"/*.apk" ) # revisit for case sensitivity and forward/backslash compatability

    # get a list of device IDs for all attached tablets
    devices = []
    p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        # device_id = re.match( '^([%&+ \w]+).*device$', line )
        device_id = re.match( '^([%&+ \w]+)\s+.*$', line.decode("latin1") )
        # for each device, install the APKs one by one
        if device_id is not None:
            devices.append(device_id.group(1))
    retval = p.wait()
    
    # setup the pool
    pool = Pool(processes=len(devices)) # argument is number of processes, default is the number of CPUs
    # pool = Pool()
    for device_id in devices:
        if device_id is not None:
            print ( "Using tablet %s" % device_id)
            if flash:
                # no callback, ignoring return codes
                res = pool.apply_async( flashTablet, args = ( device_id, fastboot, bootloader, android_image ))
                time.sleep(1) # stagger by 1 second
            else:
                res = pool.apply_async( installAPKs, args = ( device_id, apks, ), callback=checkReturnCode)
    pool.close()

    # OS/X and Windows seem to be behaving differently - not sure if this is correct
    # but pool.join() seems to block on my Windows 7 test machine
    if ( posix ):
        pool.join()
        
    #try:
    #    s = res.get( 360 ) # 6 min timeout, sufficient?
    #except Pool.TimeoutError:
    #    pool.terminate()
    
    # sys.stdout.flush()
    
    elapsed_time = str(datetime.timedelta(seconds=(time.time() - start_time)))
    # print( '%s completed - %s tablet(s) in %.03f\n' % ( sys.argv[0], len(devices), float(elapsed_time) ))
    print( '%s completed - %s tablet(s) in %s\n' % ( sys.argv[0], len(devices), elapsed_time ))
