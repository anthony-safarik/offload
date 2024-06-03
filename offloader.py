'''
00 landing
01 offloaded
02 transfered
03 backed up
04 md5 checked
'''

import os
import shutil
import subprocess
import time
from datetime import datetime
from walker import FileWalker

now = time.strftime("%y%m%d_%H%M%S")

def get_file_paths(inpath):
    '''
    get paths from inpath
    '''
    for (path,dirs,files) in os.walk(inpath):
        for item in files:
                yield os.path.join(path,item)

def meets_conditions(text):
    extensions=('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mkv', 'arw')
    if os.path.basename(text).startswith('.'):
        return False
    if not text.lower().endswith(extensions):
        return False
    return True
    

def is_dated(text):
    #20221205-
    if len(text) < 9:
        return False
    for char in text[0:7]:
        if not char.isdigit():
            return False
    if text[8] != '-':
        return False
    return True


def copy_file_dated(src, dst):
    modified_time = os.path.getmtime(src)
    date_modified = datetime.fromtimestamp(modified_time)
    year = date_modified.strftime("%Y")
    date = date_modified.strftime("%Y-%m-%d")
    destination_year_folder = os.path.join(dst, year)
    destination_date_folder = os.path.join(destination_year_folder, date)
    if not os.path.exists(destination_date_folder):
        os.makedirs(destination_date_folder)

    fname = os.path.basename(src)

    if is_dated(fname):
        file = fname
    else:
        file = date_modified.strftime("%Y%m%d-")+fname

    destination_file_path = os.path.join(destination_date_folder, file)
    undated_destination_file_path = os.path.join(destination_date_folder, fname)

    if os.path.exists(undated_destination_file_path):
        print(f'version of {fname} exists in the target path')
    elif os.path.exists(destination_file_path):
        print(f'version of {fname} exists as {file} in the target path')
    elif not os.path.exists(destination_file_path):
        shutil.copy2(src, destination_file_path)
        print(f"Copied:\n     {src}\n-->  {destination_file_path}\n")

def rsync_dated_photo(src, dst):
    modified_time = os.path.getmtime(src)
    date_modified = datetime.fromtimestamp(modified_time)
    year = date_modified.strftime("%Y")
    date = date_modified.strftime("%Y-%m-%d")
    destination_year_folder = os.path.join(dst, year)
    destination_date_folder = os.path.join(destination_year_folder, date)
    if not os.path.exists(destination_date_folder):
        os.makedirs(destination_date_folder)

    fname = os.path.basename(src)

    if is_dated(fname):
        file = fname
    else:
        file = date_modified.strftime("%Y%m%d-")+fname

    destination_file_path = os.path.join(destination_date_folder, file)
    undated_destination_file_path = os.path.join(destination_date_folder, fname)

    if os.path.exists(undated_destination_file_path):
        print(f'version of {fname} exists in the target path')
    elif os.path.exists(destination_file_path):
        print(f'version of {fname} exists as {file} in the target path')
    elif not os.path.exists(destination_file_path):
        # shutil.copy2(src, destination_file_path)
        subprocess.run(['rsync', '-a', src, destination_file_path])
        print(f"Copied:\n     {src}\n-->  {destination_file_path}\n")

def rsync_dated_photos(src, dst):
    # Get a list of files meeting conditions
    full_file_paths = [x for x in get_file_paths(src) if meets_conditions(x)]
    # Do rsync
    for fpath in full_file_paths:
        rsync_dated_photo(fpath, dst)

if __name__ == "__main__":
    source_directory = input("Enter the photos source dir: ")
    target_directory = input("Enter the photo copy dir: ")
    os.makedirs(target_directory, exist_ok=True)

    rsync_dated_photos(source_directory, target_directory)

    walker = FileWalker(source_directory)
    walker.walk_directory()

    walker2 = FileWalker(target_directory)
    walker2.walk_directory()

    print('********************COMPARE MD5************************')
    # input('PAUSED.. hit return to continue')
    
    # Compare file metadata
    walker.get_file_info()
    walker2.get_file_info()

    print (f'\nSizes do not match:\n{walker.size_unequal(walker2)}\n')

    walker.get_file_md5()
    walker2.get_file_md5()

    # Write file info to csv file
    
    dicts_for_csv = list(walker.file_info.values())
    walker.write_dicts_to_csv(dicts_for_csv, str(walker.source_path)+'_FILE_INFO_'+now+'.csv')
    dicts_for_csv2 = list(walker2.file_info.values())
    walker2.write_dicts_to_csv(dicts_for_csv2, str(walker2.source_path)+'_FILE_INFO_'+now+'.csv')

    walker_keys = list(walker.file_hashes.keys())
    walker2_keys = list(walker2.file_hashes.keys())

    print (f'\nFiles missing from {target_directory}')
    print(list(x for x in walker_keys if x not in walker2_keys))

    print('Offload Completed')