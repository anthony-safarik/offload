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
                        'File Path': file_path, #file path is the posix path object
                        'Bytes': int(bytes)
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
                            'File Path': file_path, #file path is the posix path object
                            'Bytes': int(bytes)
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

    def diff_file_info(self,other, info_type):
        this_file_info = [inner_dict.get(info_type) for inner_dict in self.file_info.values() if info_type in inner_dict]
        other_file_info = [inner_dict.get(info_type) for inner_dict in other.file_info.values() if info_type in inner_dict]
        for i in this_file_info:
            print(i,type(i))
        for i in other_file_info:
            print(i,type(i))
        diff_list = list(set(other_file_info)-set(this_file_info))
        return diff_list
    
    def time_it(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Function {func.__name__} took {end_time - start_time} seconds to run.")
            return result
        return wrapper


    @property
    def file_paths(self):
        return [inner_dict.get("File Path") for inner_dict in self.file_info.values() if "File Path" in inner_dict]
    
    @property
    def file_hashes(self):
        return [inner_dict.get("MD5") for inner_dict in self.file_info.values() if "MD5" in inner_dict]



    @time_it
    def get_file_md5(self):
        total_calc_bytes = 0
        # for file_path in self.file_paths.values():
        for file_path in self.file_paths:
            full_file_path = str(file_path.resolve())
            # Calculate the MD5 hash
            file_hash = self.calculate_md5(full_file_path)
            # Get the relative path
            relative_path = str(file_path.relative_to(self.input_source))

            # Use setdefault to create / update the dictionary entry
            file_info_dict = self.file_info.setdefault(relative_path, {})
            file_info_dict.update({
                'MD5': file_hash
            })
            total_calc_bytes += file_path.stat().st_size
            print(f"{str(100 * float(total_calc_bytes)/float(self.total_size)).split('.')[0]}% of hashes calculated... ({total_calc_bytes} of {self.total_size} bytes) ")



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

    walker = PathWalker(source_directory)
    walker.walk_path()
    dicts_for_csv = list(walker.file_info.values())

    walker2 = PathWalker(compare_directory)
    walker2.walk_path()
    dicts_for_csv2 = list(walker2.file_info.values())

    print (f'\nsource: {walker.input_source}\ncount: {walker.file_count}\nsize: {walker.total_size}')
    print (f'\ncompare: {walker2.input_source}\ncount: {walker2.file_count}\nsize: {walker2.total_size}')
    
