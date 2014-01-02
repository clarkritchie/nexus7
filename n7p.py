#!/usr/local/bin/python3
#
# Author:  Clark Ritchie
# Date:    December, 2013
# Repo:    https://github.com/clarkritchie/nexus7
#
# A simple cross-platform Python script to:
# - Upgrade and/or Patch N-attached Android tablets connected via a USB hub
# - Install apps on N-attached Android tablets connected via a USB hub
# - Copy files onto N-attached Android tablets connected via a USB hub
#
# Usage:  python3 n7p.py -h
#
# Running n7p.py version 1.3.1
# usage: n7p.py [-h] [-c CONFIG] [-u] [-p] [-a] [-f]
#
# optional arguments:
#  -h, --help            show this help message and exit
#  -c CONFIG, --config CONFIG
#                        Use alternate configuration file (Default: n7.ini)
#
# Choose one of the operations below:
#  -u, --upgrade         Upgrade Android OS on all connected tablets (using
#                        fastboot)
#  -p, --patch           Patch Android OS on all connected tablets (using adb
#                        sideload)
#  -a, --apps            Install apps on all connected tablets (using adb
#                        install)
#  -f, --files           Copy files to all connected tablets (using adb push)
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

import subprocess, sys, re, time, glob, datetime, os, argparse
# @see http://stackoverflow.com/questions/7207309/python-how-can-i-run-python-functions-in-parallel
from multiprocessing import Pool

VERSION="1.3.2"
CONFIG_FILE = 'n7.ini'

# check if we're on a posix or Windows machine
#posix = 1
#if ( os.name == "nt"): # not sure what other versions of Windows report here?
#    posix = 0

# ******************************************************************************
# Simple configuration file parser, taken from:
# http://www.decalage.info/en/python/configparser
# ******************************************************************************
class ParseINI(dict):
  def __init__(self, f):
    self.f = f
    self.__read()
 
  def __read(self):
    with open(self.f, 'r') as f:
      slovnik = self
      for line in f:
        if not line.startswith("#") and not line.startswith(';') and line.strip() != "":
          line = line.replace('=', ':')
          line = line.replace(';', '#')
          index = line.find('#')
          line = line[:index]
          line = line.strip()
          if line.startswith("["):
            sections = line[1:-1].split('.')
            slovnik = self
            for section in sections:
              if section not in slovnik:
                slovnik[section] = {}
              slovnik = slovnik[section]
          else:
            if not self:
              slovnik['global'] = {}
              slovnik = slovnik['global']
            parts = line.split(":", 1)
            slovnik[parts[0].strip()] = parts[1].strip()
 
  def items(self, section):
    try:
      return self[section]
    except KeyError:
      return []
    
# ******************************************************************************
# upgradeTablet
# This function will ...
# ******************************************************************************
def upgradeTablet( device_id, fastboot, bootloader, android_image ):
    r = 0
    sleep = 10
    print( 'Begin upgrade of tablet %s'  % device_id )
    
    upgrade_cmds = [
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
    for cmd in upgrade_cmds:
        # sleep for 10 sec while the bootloader reboots
        print( 'Step #%s' % n)
        
        if n == 8:
            print ( 'Sleeping for %s...\r\n' % sleep )
            time.sleep(sleep)
        
        # output command to STDOUT
        print( ' '.join(map(str, cmd)) )
        time.sleep(1)
        subp = subprocess.Popen( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr = subp.communicate()
        subp.wait()
        print(stdout.decode())
        print(stderr.decode())
        n += 1

    print ( 'End upgrade of tablet %s' % device_id )
    return r

# ******************************************************************************
# patchTablet
# This function will ...
# ******************************************************************************
def patchTablet( device_id, adb, patch_file ):
    r = 0
    sleep = 10
    print( 'Begin patch of tablet %s' % device_id )

    cmd='%s -s %s sideload %s' % ( adb, device_id, patch_file )
    print( cmd )
    # subp = subprocess.Popen( [adb,"-s",device_id,"sideload",patch_file], bufsize=4096 )
    subp = subprocess.Popen( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    stdout, stderr = subp.communicate()
    subp.wait()
    print(stdout.decode())
    print(stderr.decode())

    print ( 'End patch of tablet %s' % device_id )
    print ( '\n(Your tablet will now verify the OS patch, this may take a few minutes...)' )
    return r

# ******************************************************************************
# installApps
# This function will install all APK files in a given directory onto all
# connected tablets
# ******************************************************************************
def installApps( device_id, adb, apks ):
    r = 0
    print ( 'Begin APK install on tablet %s' % device_id )
    for f in apks:
        print( 'Installing %s onto %s' % ( f, device_id ))
        # cmd=adb + ' -s '+device_id+" install -r "+f
        # print(cmd)
        subp = subprocess.Popen( [adb,"-s",device_id,"install","-r",f], bufsize=4096, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        subp.communicate()
        r = subp.returncode
        subp.wait()
    print( 'End APK install on tablet %s' % device_id )
    return r

def copyFiles( device_id, adb, filename, path ):
    r = 0
    dest=path+"/"+os.path.basename(filename)
    print ( 'Begin file copy %s to %s on tablet %s' % ( filename, dest, device_id ) )
    subp = subprocess.Popen( [adb,"-s",device_id,"push",filename,dest] )
    subp.communicate()
    r = subp.returncode
    subp.wait()
    print ( 'End file copy on tablet %s' % device_id )
    return r

# for testing subprocess exit problems on Windows 7
# def installAPKs_wrapped( device_id, apks ):
#    try:
#        installAPKs( device_id, apks )
#    except:
#        print('%s' % (traceback.format_exc()))

def checkReturnCode(r):
    print("Return code: %s" % r)

# ******************************************************************************
# Main
# ******************************************************************************
if __name__ == '__main__':
    
    start_time = time.time()
    
    print( 'Running %s version %s' % ( os.path.basename(__file__), VERSION ))
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '-c', '--config', metavar = 'CONFIG', type = str, help = 'Use alternate configuration file (Default: %s)' % CONFIG_FILE )
    group = parser.add_argument_group( 'Choose one of the operations below' )
    
    group.add_argument( '-u', '--upgrade',action='store_true', default=False,help='Upgrade Android OS on all connected tablets (using fastboot)' )
    group.add_argument( '-p', '--patch',action='store_true', default=False,help='Patch Android OS on all connected tablets (using adb sideload)' )
    group.add_argument( '-a', '--apps',action='store_true', default=False,help='Install apps on all connected tablets (using adb install)' )
    group.add_argument( '-f', '--files',action='store_true', default=False,help='Copy files to all connected tablets (using adb push)' )
    
    output = parser.parse_args()
    # check if the passed an alt. config file
    if output.config is not None:
        CONFIG_FILE = output.config
    # print('Output %s' % output.config)
    
    # if they specified an alternate cofiguration file, use it
    # if not output.config:
    if os.path.exists( CONFIG_FILE ):
        # need to check that this file exists, maybe turn it into an argument
        # ini = ParseINI( str(sys.argv[1]) )
        print("Using %s config file" % CONFIG_FILE )
        ini = ParseINI( CONFIG_FILE )
        adb = ini['nexus7']['adb'].replace("'", "")
        fastboot = ini['nexus7']['fastboot'].replace("'", "")
        apk_files = ini['nexus7']['apk_files'].replace("'", "")
        android_image = ini['nexus7']['android_image'].replace("'", "")
        bootloader = ini['nexus7']['bootloader'].replace("'", "")
        patch_file = ini['nexus7']['patch'].replace("'", "")
        file1 = ini['files']['file1'].replace("'", "")
        file2 = ini['files']['file2'].replace("'", "")
        file3 = ini['files']['file3'].replace("'", "")
        file4 = ini['files']['file4'].replace("'", "")
        file5 = ini['files']['file5'].replace("'", "")
    else:
        print( 'Error!  Config file %s does not exist' % CONFIG_FILE )
        sys.exit(0)
    
    upgrade=False
    patch=False
    apps=False
    files=False
    
    if output.upgrade:
        upgrade=True
        cmd=fastboot + " devices"
        print( 'Upgrade Android OS on all attached tablets' )
    elif output.patch:
        patch=True
        cmd=adb + " devices"
        print( 'Patch Android OS on all attached tablets' )
    elif output.apps:
        apps=True
        cmd=adb + " devices"
        # get all the APKs into a list
        if os.path.exists( apk_files ):
            apks = glob.glob( apk_files+"/*.apk" ) # check case sensitivity, slash compatability
            print( 'Install apps on attached tablets' )
        else:
            print( 'Error!  APK directory %s does not exist' % apk_files )
            sys.exit(0)        
    elif output.files:
        files=True
        cmd=adb + " devices"
        print( 'Install files on attached tablets' )
    else:
        parser.print_help()
        sys.exit(0)

    print( '\n***************************************************************' )
    print( 'adb: %s' % adb )
    print( 'fastboot: %s' % fastboot )
    print( 'APK directory: %s' % apk_files )
    print( 'Android OS image: %s' % android_image )
    print( 'Android bootloader: %s' % bootloader )
    print( 'Android patch: %s' % patch_file )
    print( '***************************************************************\n' )

    # get a list of device IDs for all attached tablets
    devices = []
    p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        device_id = re.match( '^([0-9a-fA-F]+)\s+.*$', line.decode("latin1") )
        # for each device, install the APKs one by one
        if device_id is not None:
            devices.append(device_id.group(1))
    retval = p.wait()
    
    if len(devices) == 0:
        print( 'Error!  No tablet(s) found or tablet(s) are not ready' )
        sys.exit(0)
              
    # setup the pool
    pool = Pool(processes=len(devices)) # argument is number of processes, default is the number of CPUs
    # pool = Pool()
    for device_id in devices:
        if device_id is not None:
            print ( "Using tablet %s" % device_id)
            if upgrade:
                # no callback, ignoring return codes
                res = pool.apply_async( upgradeTablet, args = ( device_id, fastboot, bootloader, android_image ))
                time.sleep(1) # stagger by 1 second
            elif patch:
                # no callback, ignoring return codes
                res = pool.apply_async( patchTablet, args = ( device_id, adb, patch_file ))
                time.sleep(1) # stagger by 1 second
            elif apps:
                res = pool.apply_async( installApps, args = ( device_id, adb, apks, ), callback=checkReturnCode )
            elif files:
                n = 1
                # for f in [file1,file2,file3,file4,file5,file6,file7,file8,file9]:
                for filename in [file1,file2,file3,file4,file5]:
                    f = filename.split(',')[0] # filename
                    p = filename.split(',')[1] # path
                    if os.path.isfile(f):
                        copyFiles( device_id, adb, f, p )
            else:
                print( '\r\nNothing to do!\r\n' )
    pool.close()

    # OS/X and Windows seem to be behaving differently - not sure if this is correct
    # but pool.join() seems to block on my Windows 7 test machine
    #if ( posix ):
    #    pool.join()
    pool.join()
    
    elapsed_time = str(datetime.timedelta(seconds=(time.time() - start_time)))
    # print( '%s completed - %s tablet(s) in %.03f\n' % ( sys.argv[0], len(devices), float(elapsed_time) ))
    print( '%s version %s completed %s tablet(s) in %s\n' % ( os.path.basename(__file__), VERSION, len(devices), elapsed_time ))