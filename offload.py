from pathlib import Path
import os
import time
import datetime
import sys

class FileWalker:
    def __init__(self, source_path):
        self.source_path = Path(source_path)
        self.file_paths = {}
        self.file_info = {}

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

#########################################################################################
    @time_it
    def get_file_info(self):
        for file_path in self.file_paths.values():
            full_file_path = str(file_path.resolve())
            file_size = file_path.stat().st_size
            mtime = file_path.stat().st_mtime
            timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

            file_info_dict = {'File Path': full_file_path,
                          'Bytes': file_size,
                          'Date': timestamp_str}

            self.file_info[str(file_path.relative_to(self.source_path))] = file_info_dict

        # for info_dict in self.file_info.values(): print (info_dict)

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