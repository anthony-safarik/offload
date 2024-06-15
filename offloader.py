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
import hashlib

now = time.strftime("%y%m%d_%H%M%S")

def rsync_file(src, dst):
    """Copy file with attributes using rsync"""
    subprocess.run(['rsync', '-a', src, dst])

def sync_subfolders(src, dst):
    """Copy each file in folder, maintaining structure"""
    for item in get_file_paths(src):
        target = item.replace(src,dst)
        target_dir = os.path.dirname(target)
        os.makedirs(target_dir, exist_ok=True)
        rsync_file(item, target)

def sync_top_level_files(src, dst):
    """Copy each file in one flat folder to another"""
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isfile(item_path):
            target_path = os.path.join(dst, item)
            rsync_file(item_path, target_path)

def get_file_paths(inpath):
    '''
    get paths from inpath
    '''
    for (path,dirs,files) in os.walk(inpath):
        for item in files:
                yield os.path.join(path,item)

def meets_conditions(text):
    extensions=('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mkv', 'arw', 'mov')
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

def rsync_flat_dates(src, dst):
    '''
    copies the src file to dst folder, renaming it to YYYYMMDD-file.ext format
    '''

    modified_time = os.path.getmtime(src)
    date_modified = datetime.fromtimestamp(modified_time)
    fname = os.path.basename(src)

    if is_dated(fname):
        new_fname = fname
    else:
        new_fname = date_modified.strftime("%Y%m%d-")+fname

    new_fpath = os.path.join(dst,new_fname)

    if not os.path.exists(new_fpath):
        os.makedirs(dst, exist_ok=True)
        subprocess.run(['rsync', '-a', src, new_fpath])
        print(f"Copied:\n     {src}\n-->  {new_fpath}\n")

def walk_scr_and_copy_all_media_to_dst_in_flat_dated_format(src,dst):
    '''
    does what is says
    '''
    full_file_paths = [x for x in get_file_paths(src) if meets_conditions(x)]
    for fpath in full_file_paths:
        rsync_flat_dates(fpath, dst)

def rsync_dated_photo(src, dst):
    '''
    gets modified time from src file and copies it to dst folder following the dated structure
    while checking whether there is already a representation of a file in that folder (dated or not)
    '''
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
    '''
    Walks scr directory and copies photos in dated pattern to dst
    '''
    # Get a list of files meeting conditions
    full_file_paths = [x for x in get_file_paths(src) if meets_conditions(x)]
    # Do rsync
    for fpath in full_file_paths:
        rsync_dated_photo(fpath, dst)

def calculate_md5(file_path):
    """Calculate the MD5 hash of a file."""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def create_sidecar_file(dst_path, sidecar_string, ext='md5'):
    """Create a sidecar file with sidecar_string, such as MD5"""
    sidecar_path = f"{dst_path}.{ext}"
    with open(sidecar_path, "w") as sidecar_file:
        sidecar_file.write(sidecar_string)
    return sidecar_path

def read_sidecar_file(file_path):
    """
    reads text string contents from file_path returns string
    """
    contents = None

    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            contents = file.read()
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except IOError:
        print(f"An error occurred while reading the file {file_path}.")

    return(contents)

def gen_sidecars_recursive(inpath):
    for fpath in get_file_paths(inpath):
        fchecksum = calculate_md5(fpath)
        sidecar_path = create_sidecar_file(fpath, fchecksum)
        side_md5 = read_sidecar_file(sidecar_path)
        # print(fchecksum, side_md5)

def read_sidecars_recursive(inpath, ext='.md5'):
    sidecar_list = []
    for fpath in get_file_paths(inpath):
        if fpath.endswith(ext):
            contents = read_sidecar_file(fpath)
            if contents:
                ftuple = (fpath, contents)
                sidecar_list.append(ftuple)
    return sidecar_list

def filter_tuples(master_list, subset_list):
    # Extract the second elements from the subset_list tuples
    subset_keys = {item[1] for item in subset_list}
    
    # Filter the master_list tuples
    result = [item for item in master_list if item[1] not in subset_keys]
    
    return result

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
    # print(list(x for x in walker_keys if x not in walker2_keys))

    print('Offload Completed')