from pathlib import Path
import os
import time
import datetime
import sys
import hashlib
import csv

class FileWalker:
    def __init__(self, source_path):
        self.source_path = Path(source_path)
        self.file_paths = {}
        self.file_info = {}
        self.file_hashes = {}

    def time_it(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Function {func.__name__} took {end_time - start_time} seconds to run.")
            return result
        return wrapper

    @time_it
    def walk_directory(self):
        for root, dirs, files in os.walk(self.source_path):
            for file_name in files:
                if file_name != '.DS_Store' and file_name != '._.DS_Store':
                    file_path = Path(root) / file_name
                    # self.file_paths[str(file_path)] = file_path
                    self.file_paths[str(file_path.relative_to(self.source_path))] = file_path

    def print_file_paths(self):
        for file_path in self.file_paths.values():
            print(f'{file_path.relative_to(self.source_path)} --- {file_path.stat()}')

    @time_it
    def print_modified_time(self):
        for file_path in self.file_paths.values():
            mtime = file_path.stat().st_mtime
            timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            print(f'{file_path.relative_to(self.source_path)} --- {timestamp_str}')

    @time_it
    def get_file_info(self):
        for file_path in self.file_paths.values():
            full_file_path = str(file_path.resolve())
            file_size = file_path.stat().st_size
            mtime = file_path.stat().st_mtime
            timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

            # Get the relative path
            relative_path = str(file_path.relative_to(self.source_path))

            # Use setdefault to create / update the dictionary entry
            file_info_dict = self.file_info.setdefault(relative_path, {})
            file_info_dict.update({
                'File Path': full_file_path,
                'Bytes': file_size,
                'MD5': '',
                'Date': timestamp_str
            })

    @time_it
    def get_file_md5(self):
        for file_path in self.file_paths.values():
            full_file_path = str(file_path.resolve())
            # Calculate the MD5 hash
            file_hash = self.calculate_md5(full_file_path)
            # Get the relative path
            relative_path = str(file_path.relative_to(self.source_path))

            # Use setdefault to create / update the dictionary entry
            file_info_dict = self.file_info.setdefault(relative_path, {})
            file_info_dict.update({
                'MD5': file_hash
            })

            # Add file_info_dict to file_hashes dict: {MD5: [{file_info_dict}]}
            if file_hash not in self.file_hashes:
                self.file_hashes[file_hash] = [file_info_dict]
            else:
                self.file_hashes[file_hash].append(file_info_dict)
#########################################################################################
    def write_dicts_to_csv(self, data_list, filename):
        """
        Writes a list of dictionaries to a CSV file.

        Args:
            data_list (list[dict]): List of dictionaries containing data.
            filename (str): Name of the CSV file to create.

        Returns:
            None
        """
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = data_list[0].keys() if data_list else []
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data_list:
                    writer.writerow(row)
            print(f"Data written to {filename} successfully!")
        except Exception as e:
            print(f"Error writing to {filename}: {e}")


    def print_types(*args):
        for arg in args:
            # print(f"Type of {arg}: {type(arg).__name__}")
            print(f"Type: {type(arg).__name__}")

#########################################################################################
    def file_paths_match(self, other):
        return sorted(self.file_paths.keys()) == sorted(other.file_paths.keys())
    
    def minus(self, other):
        return [x for x in self.file_paths.keys() if x not in other.file_paths.keys()]
    
    def size_unequal(self, other):
        unequal_path_keys = []
        for x in self.file_info.keys():
            if x in other.file_info.keys():
                if self.file_info[x]['Bytes'] != other.file_info[x]['Bytes']:
                    unequal_path_keys.append(x)
        return unequal_path_keys
    
    def md5_unequal(self, other):
        unequal_path_keys = []
        for x in self.file_info.keys():
            if x in other.file_info.keys():
                if self.file_info[x]['MD5'] != other.file_info[x]['MD5']:
                    unequal_path_keys.append(x)
        return unequal_path_keys

    @staticmethod
    def calculate_md5(file_path):
        """Calculate the MD5 hash of a file."""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

# Example usage
if __name__ == "__main__":

    if len(sys.argv) > 1:
        source_directory = sys.argv[1]
    else:
        source_directory = input("Enter the source path: ")

    if len(sys.argv) > 2:
        compare_directory = sys.argv[2]
    else:
        compare_directory = input("Enter the compare path: ")




    walker = FileWalker(source_directory)
    walker.walk_directory()

    # Compare file paths
    walker2 = FileWalker(compare_directory)
    walker2.walk_directory()

    print (f'\nExtra files in {source_directory} \n {walker.minus(walker2)}\n')
    print (f'\nExtra files in {compare_directory} \n {walker2.minus(walker)}\n')

    print(f'File paths are a perfect match?: {walker.file_paths_match(walker2)}')

    # Compare file metadata
    walker.get_file_info()
    walker2.get_file_info()

    print (f'\nSizes do not match:\n{walker.size_unequal(walker2)}\n')

    # walker.get_file_md5()
    # walker2.get_file_md5()

    # print (f'MD5 do not match:\n{walker.md5_unequal(walker2)}\n')

    print('********************************************')
    dicts_for_csv = list(walker.file_info.values())
    # print(len((dicts_for_csv),'/Users/tonysafarik/_scratch/output.csv'))
    walker.write_dicts_to_csv(dicts_for_csv, str(walker.source_path)+'_FILE_INFO.csv')

    #CHECK WHICH FILES ARE DUPES. TODO>REDUCE REDUNDANCY BETWEEN FILE INFO AND FILE HASHES
    # for key in walker.file_hashes.keys():
    #     print (key, len(walker.file_hashes[key]))
    #     if len(walker.file_hashes[key]) > 1:
    #         print (walker.file_hashes[key])