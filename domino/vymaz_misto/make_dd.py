#!/usr/local/bin/python2.7

import os
import sys
import copy
import argparse
import subprocess

utility_path_dd = '/bin/dd'
utility_path_df = '/bin/df'

parser = argparse.ArgumentParser()
parser.add_argument("-m", action="store", dest="mountpoint", default='/mnt/notes', type=str, help="mountpoint to filesystem, e.g /mnt/notes, or root filesystem /, default is /mnt/notes mountpoint")
parser.add_argument("-f", action="store", dest="tmp_file", default='temporary.txt', type=str, help="name of temporary file - e.g temporary.txt, default is temporary.txt")
parser.add_argument("-s", action="store", dest="minus_size", default='10', type=int, help="size without erase in GB, default is 10")
parser.add_argument("-b", action="store", dest="bs_size", default='64', type=int, help="block size in dd parameter bs in megabytes, default is 64")
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
results = parser.parse_args()
#parser.parse_args()

def exists_utility(program_name):
    '''Testing utility path exists
    
    Keyword arguments:
    program_name -- name of program what we testing

    Returns: True or False 
    '''

    if os.path.isfile(program_name) and os.access(program_name, os.X_OK):
        return True
    else:
        return False

def checking_exists_utility(program_name):
    '''Print information about utility path exists

    Keyword arguments:
    program_name -- name of program what we testing

    Returns:Print information about utility existing
    '''
    if exists_utility(program_name):
        print('{0} utility path: OK'.format(os.path.basename(program_name)))
    else:
        print('{0} utility path: NO - please write right path to this script'.format(os.path.basename(program_name)))
        sys.exit(1)

def exists_mountpoint(mountpoint):
    '''Testing mountpoint path exists

    Keyword arguments:
    mountpoint -- path to mountpoint where we testing exists 

    Returns: True or False
    '''

    if os.path.ismount(mountpoint):
        return True
    else:
        return False

def checking_exists_mountpoint(mountpoint):
    '''Print information about mountpoint path exists

    Keyword arguments:
    mountpoint -- name of program what we testing

    Returns:Print information about mountpoint existing
    '''
    if exists_mountpoint(mountpoint):
        print('{0} mountpoint path: OK'.format(mountpoint))
    else:
        print('{0} mountpoint path: NO - please write right mountpoint parameter -m to this script'.format(mountpoint))
        sys.exit(1)

def print_mountpoint_information(mountpoint):
    try:
        command_df = utility_path_df + ' -h ' + mountpoint
        vysledok = subprocess.check_output(command_df, shell=True)
        print('MOUNTPOINT {0} INFORMATION:').format(mountpoint)
        print vysledok
    except:
        print ("ERROR: I can't obtain information about mountpoint {0}").format(mountpoint)
        sys.exit(1)

def disk_usage(mountpoint):
    """Return disk usage associated with path."""
    st = os.statvfs(mountpoint)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    #dict(zip(['one', 'two', 'three'], [1, 2, 3]))
    return dict(zip(['total_bytes', 'free_bytes', 'used_bytes', 'usage_percent'], [total, free, used, percent]))

def make_dd(bs_size, count, if_parameter='/dev/zero', of_parameter='/temporary.txt'):
    '''Make dd utility on mountpoint

    Keyword arguments:
    mountpoint -- path to mountpoint where we testing exists
    bs_size -- block size in dd parameter bs - in megabytes
    count -- how many count a bs_size

    Returns:make dd with parameters and True or False
    '''
    command_dd = utility_path_dd + ' bs=' + str(bs_size) + 'M' + ' count=' + str(count) + ' if=' + if_parameter + ' of=' + of_parameter
    print command_dd
    try:
        output_command = subprocess.check_output(command_dd, shell=True)
        return True, output_command
    except subprocess.CalledProcessError:
        print('!!!Nemuzu vykonat program dd !!!')
        sys.exit(1)

def make_sync():
    '''Make sync system utility'''
    try:
        output = subprocess.call('sync') 
        return True
    except CalledProcessError:
        print('!!!Nemuzu vykonat sync !!!')
        sys.exit(1)

def delete_file(file):
    '''delete file'''
    try:
        if os.path.isfile(file):
            os.remove(file) 
            return True
        else:
            print('zadane meno nie je subor')
            return False
    except OSError:
        print('Nemuzu smazat soubor {0}, smaz ho rucne').format(file) 
        sys.exit(1)





mountpoint_parameters = disk_usage(results.mountpoint)
write_bytes = mountpoint_parameters['free_bytes'] - (results.minus_size * 1024 * 1024 * 1024)
count = int(round(((write_bytes / (1024 * 1024)) / results.bs_size)))
temporary_file = os.path.join(results.mountpoint, results.tmp_file)


print('------------------------------------')
print('CHECKING SCRIPT PARAMETERS')
print('------------------------------------')
checking_exists_utility(utility_path_dd)
checking_exists_utility(utility_path_df)
checking_exists_mountpoint(results.mountpoint)
print('SCRIPT PARAMETERS OK')

print("\n")

print('------------------------------------')
print('MOUNTPOINT INFORMATION BEFORE dd')
print('------------------------------------')
print disk_usage(results.mountpoint)

print("\n")

print('------------------------------------')
print('DD UTILITY PARAMETERS')
print('------------------------------------')
print('temporary file: {0}').format(temporary_file)
print('block size bs={0}M').format(results.bs_size)
print('count in dd is count={0}').format(count)

print("\n")

print('------------------------------------')
print('Must be patient, write with dd utility is long time operation')
print('------------------------------------')
make_dd(results.bs_size, count, of_parameter=temporary_file)

print("\n")

print('------------------------------------')
print('MOUNTPOINT INFORMATION AFTER dd')
print('------------------------------------')
print disk_usage(results.mountpoint)

print("\n")

print('------------------------------------')
print('REMOVING TEMPORARY FILE {0}').format(temporary_file)
print('------------------------------------')
if delete_file(temporary_file):
    print('deleting file {0}: OK').format(temporary_file)

print("\n")

print('------------------------------------')
print('MOUNTPOINT INFORMATION AFTER REMOVING TEMPORARY FILE')
print('------------------------------------')
make_sync()
print disk_usage(results.mountpoint)

print("\n") 
