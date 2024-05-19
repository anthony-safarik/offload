import os
import shutil
from datetime import datetime

# SOURCE = '/Volumes/Untitled/DCIM'
SOURCE = '/Volumes/Untitled/DCIM'
TARGET = '/Volumes/ORICO/INCOMING/PHOTOS'
os.makedirs(TARGET, exist_ok=True)

def crawl_dir(inpath,file_ending=''):
    '''
    inpath is a string representing a DIRECTORY on the file system
    file_ending is a string matching end of file name
    returns a sorted list of files from inpath
    '''
    filepath_list=[]
    for (path,dirs,files) in os.walk(inpath):
        for item in files:
            if item.endswith(file_ending):
                filepath = os.path.join(path,item)
                if filepath not in filepath_list:
                    filepath_list.append(filepath)
    return sorted(filepath_list)

def meets_conditions(text):
    extensions=('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mkv', 'arw')
    if text.startswith('.'):
        return False
    if not text.lower().endswith(extensions):
        return False
    return True
    
#Check if file is something we want to copy and make list
file_names = [x for x in crawl_dir(SOURCE) if meets_conditions(x)]

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


def copy_file_dated(test_file_path, TARGET):
    modified_time = os.path.getmtime(test_file_path)
    date_modified = datetime.fromtimestamp(modified_time)
    year = date_modified.strftime("%Y")
    date = date_modified.strftime("%Y-%m-%d")
    destination_year_folder = os.path.join(TARGET, year)
    destination_date_folder = os.path.join(destination_year_folder, date)
    if not os.path.exists(destination_date_folder):
        os.makedirs(destination_date_folder)

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
        shutil.copy2(test_file_path, destination_file_path)
        print(f"Copied:\n     {test_file_path}\n-->  {destination_file_path}\n")

for fname in file_names:
    copy_file_dated(os.path.join(SOURCE,fname), TARGET)

print('Offload Completed')