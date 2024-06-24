from pathlib import Path
import os
import time
import datetime
import sys
import hashlib
import csv


class PathWalker:
    def __init__(self, input_source):
        self.input_source = input_source
        self.file_info = {}
        self.file_count = 0
        self.total_size = 0

    def read_csv_special(self):
        # Interpret the source path
        if os.path.isfile(self.input_source) and self.input_source.endswith('.csv'):
            csv_name = os.path.basename(self.input_source)
            original_source_path = csv_name.replace('>','/')
            print(f'opening csv for {original_source_path}')
            # Open the CSV file
            with open(self.input_source, 'r') as file:
                # Create a DictReader object
                reader = csv.DictReader(file)

                # Iterate over each row as an OrderedDict
                for row in reader:
                    # Access values by key
                    file_path = Path(row['File Path'])
                    bytes = row['Bytes']
                    relative_path = row['Relative Path']

                    file_info_dict = self.file_info.setdefault(relative_path, row)
                    # file_info_dict = row
                    file_info_dict.update({
                        'File Path': file_path #file path is the posix path object
                            })
                    
                    self.file_count += 1
                    self.total_size += int(bytes)
        else:
            print(f'{self.input_source} not proper csv file')

    def read_csv_special_filtered(self, filter_func):
        # Interpret the source path
        if os.path.isfile(self.input_source) and self.input_source.endswith('.csv'):
            csv_name = os.path.basename(self.input_source)
            original_source_path = csv_name.replace('>','/')
            print(f'opening csv for {original_source_path}')
            # Open the CSV file
            with open(self.input_source, 'r') as file:
                # Create a DictReader object
                reader = csv.DictReader(file)

                # Iterate over each row as an OrderedDict
                for row in reader:
                    # Access values by key
                    file_path_text = row['File Path']
                    if filter_func(file_path_text):
                        file_path = Path(file_path_text)
                        bytes = row['Bytes']
                        relative_path = row['Relative Path']

                        file_info_dict = self.file_info.setdefault(relative_path, row)
                        # file_info_dict = row
                        file_info_dict.update({
                            'File Path': file_path #file path is the posix path object
                                })
                        
                        self.file_count += 1
                        self.total_size += int(bytes)
        else:
            print(f'{self.input_source} not proper csv file')

    def dump_csv(self, csv_file_path = 'default'):
        """Dumps a csv in the source path."""
        dicts_for_csv = list(self.file_info.values())
        if csv_file_path == 'default':
            csv_file_path = os.path.join(os.path.dirname(self.input_source),self.input_source.replace('/','>')+'.csv')
        self.write_dicts_to_csv(dicts_for_csv, csv_file_path)
        return csv_file_path

    def walk_path(self):
        if os.path.isdir(self.input_source):
            for root, dirs, files in os.walk(self.input_source):
                for file_name in files:
                    if not file_name.startswith('.'): #skip hidden files
                        file_path = Path(root) / file_name

                        file_size = file_path.stat().st_size
                        mtime = file_path.stat().st_mtime
                        timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y%m%d%H%M%S')
                        relative_path = str(file_path.relative_to(self.input_source))

                        # Use setdefault to create / update the dictionary entry
                        file_info_dict = self.file_info.setdefault(relative_path, {})
                        file_info_dict.update({
                            'File Path': file_path, #file path is the posix path object
                            'Source Path': self.input_source,
                            'Relative Path': relative_path,
                            'Bytes': file_size,
                            'Extension': file_path.suffix,
                            'Name': file_path.stem,
                            'MD5': '',
                            'Timestamp': timestamp_str
                        })

                        self.file_count += 1
                        self.total_size += file_size

    def walk_path_filtered(self, filter_func):
        if os.path.isdir(self.input_source):
            for root, dirs, files in os.walk(self.input_source):
                for file_name in files:
                    file_path = Path(root) / file_name
                    if filter_func(str(file_path)): #.startswith('.'): #skip hidden files

                        file_size = file_path.stat().st_size
                        mtime = file_path.stat().st_mtime
                        timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y%m%d%H%M%S')
                        relative_path = str(file_path.relative_to(self.input_source))

                        # Use setdefault to create / update the dictionary entry
                        file_info_dict = self.file_info.setdefault(relative_path, {})
                        file_info_dict.update({
                            'File Path': file_path, #file path is the posix path object
                            'Source Path': self.input_source,
                            'Relative Path': relative_path,
                            'Bytes': file_size,
                            'Extension': file_path.suffix,
                            'Name': file_path.stem,
                            'MD5': '',
                            'Timestamp': timestamp_str
                        })

                        self.file_count += 1
                        self.total_size += file_size

    @staticmethod
    def write_dicts_to_csv(data_list, filename):
        """
        Writes a list of dictionaries to a CSV file.

        Args:
            data_list (list[dict]): List of dictionaries.
            filename (str): Name of the CSV file to create.
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

class AutoWalker:
    def __init__(self, source_path):

        self.source_path = Path(source_path)
        self.file_info = {}
        self.file_count = 0
        self.total_size = 0
        self.file_signatures = []
        if os.path.isdir(source_path):
            for root, dirs, files in os.walk(self.source_path):
                for file_name in files:
                    if not file_name.startswith('.'): #skip hidden files
                        file_path = Path(root) / file_name

                        file_size = file_path.stat().st_size
                        mtime = file_path.stat().st_mtime
                        timestamp_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y%m%d%H%M%S')
                        relative_path = str(file_path.relative_to(self.source_path))

                        # Use setdefault to create / update the dictionary entry
                        file_info_dict = self.file_info.setdefault(relative_path, {})
                        file_info_dict.update({
                            'File Path': file_path, #file path is the posix path object
                            'Source Path': source_path,
                            'Relative Path': relative_path,
                            'Bytes': file_size,
                            'Extension': file_path.suffix,
                            'Name': file_path.stem,
                            'MD5': '',
                            'Timestamp': timestamp_str
                        })

                        self.file_count += 1
                        self.total_size += file_size
                        self.file_signatures.append((timestamp_str, file_size, file_path.suffix))

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

    def dump_csv(self):
        """Dumps a csv in the source path."""
        dicts_for_csv = list(self.file_info.values())
        self.write_dicts_to_csv(dicts_for_csv, str(self.source_path)+'_FILE_INFO.csv')

    def file_paths_match(self, other):
        """Returns whether two objects have mirrored file names and structure."""
        return sorted(self.file_info.keys()) == sorted(other.file_info.keys())
    
    def missing_relative_paths(self, other):
        """Return a list of relative paths that do not exist in the other walker object."""
        return [x for x in self.file_info.keys() if x not in other.file_info.keys()]
    
    def missing_file_signatures_from(self, other):
        """Return a list of signatures that do not exist in the other walker object."""
        return [x for x in self.file_signatures if x not in other.file_signatures]
    
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
    def write_dicts_to_csv(data_list, filename):
        """
        Writes a list of dictionaries to a CSV file.

        Args:
            data_list (list[dict]): List of dictionaries.
            filename (str): Name of the CSV file to create.
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

    @staticmethod
    def calculate_md5(file_path):
        """Calculate the MD5 hash of a file."""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

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

    walker = AutoWalker(source_directory)
    dicts_for_csv = list(walker.file_info.values())
    walker.dump_csv()

    walker2 = AutoWalker(compare_directory)
    dicts_for_csv2 = list(walker2.file_info.values())
    walker2.dump_csv()

    print (f'\nsource: {walker.source_path}\ncount: {walker.file_count}\nsize: {walker.total_size}')
    
    for i in walker.missing_file_signatures_from(walker2): print (i)

