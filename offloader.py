'''
00 landing
01 offloaded
02 transfered
03 backed up
04 md5 checked
'''

import os
import shutil
from datetime import datetime

SOURCE = '/Volumes/Untitled/DCIM'
TARGET = '/Volumes/CRUZER256/01_Incoming/PHOTOS'
os.makedirs(TARGET, exist_ok=True)

def get_file_paths(inpath):
    '''
    get paths from inpath
    '''
    for (path,dirs,files) in os.walk(inpath):
        for item in files:
                yield os.path.join(path,item)

def meets_conditions(text):
    extensions=('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mkv', 'arw')
    if text.startswith('.'):
        return False
    if not text.lower().endswith(extensions):
        return False
    return True
    
#Check if file is something we want to copy and make list
full_file_paths = [x for x in get_file_paths(SOURCE) if meets_conditions(x)]

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

for fpath in full_file_paths:
    copy_file_dated(fpath, TARGET)

print('Offload Completed')