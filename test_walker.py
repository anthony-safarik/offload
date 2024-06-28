import unittest
import shutil
import os
from walker import PathWalker

class TestWalker(unittest.TestCase):

    def setUp(self):
        # Create temporary folders for testing
        self.thm = 'tests/fixtures/THMBNL'
        self.test_folder = "tests/dev-test_folder"
        os.makedirs(self.test_folder, exist_ok=True)
        shutil.copytree(self.thm,os.path.join(self.test_folder,'THMBNL'))
                        
    def tearDown(self):
        # Clean up temporary folders after testing
        shutil.rmtree(self.test_folder)

    def test_walker(self):
        '''
        test walker
        '''
        # Create Walker from dir
        walker = PathWalker(self.test_folder+'/THMBNL')
        walker.walk_path() # walk it
        
        # Calculate MD5
        walker.get_file_md5()

        print (f'\nsource: {walker.input_source}\ncount: {walker.file_count}\nsize: {walker.total_size}')
        dumped_csv_fpath = walker.dump_csv() # dump it

        # Create Walker from resulting csv
        walker2 = PathWalker(dumped_csv_fpath) #set walker to a csv
        walker2.read_csv_special() # read contents in
        print (f'\nsource: {walker2.input_source}\ncount: {walker2.file_count}\nsize: {walker2.total_size}')

        # Make sure the count and size is the same
        assert int(walker.file_count) == int(walker2.file_count)
        assert int(walker.total_size) == int(walker2.total_size)


        # Define the path for the empty text file
        file_path = os.path.join(walker.input_source, 'empty_parent_file.txt')

        # Create the empty text file
        with open(file_path, 'w') as file:
            file.write('This is some noteworthy stuff right here')

        # Recreate walker object with added text tile
        walker = PathWalker(self.test_folder+'/THMBNL') #set walker to a directory
        walker.walk_path() # walk it
        print('-----unfiltered-------',walker.file_count,walker2.file_count)

        # Make sure the count and size are now not the same
        assert int(walker.file_count) == int(walker2.file_count) + 1
        assert int(walker.total_size) != int(walker2.total_size)

        # Dump csv with the added file
        new_csv_name = self.test_folder + '/csv_with_txt.csv'
        walker.dump_csv(new_csv_name)

        def meets_conditions(text):
            # text = str(posix_path)
            extensions=('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mkv', 'arw', 'mov')
            if os.path.basename(text).startswith('.'):
                print(f'{text} does not meet conditions')
                return False
            if not text.lower().endswith(extensions):
                print(f'{text} does not meet conditions')
                return False
            print(f'{text} OK')
            return True
        

        # Recreate walker object without added text tile
        walker = PathWalker(self.test_folder+'/THMBNL') #set walker to a directory
        walker.walk_path_filtered(meets_conditions) # walk it

        # Make a filtered walker from the csv
        walker3 = PathWalker(new_csv_name)
        walker3.read_csv_special_filtered(meets_conditions)

        # Make unfiltered walker from the csv
        walker4 = PathWalker(new_csv_name)
        walker4.read_csv_special()

        # Now filtered csv walker should match filtered path walker
        # Make sure the count and size is the same
        assert int(walker.file_count) == int(walker3.file_count)
        assert int(walker.total_size) == int(walker3.total_size)

        # And the unfiltered walker doesn't match
        assert int(walker.file_count) == int(walker4.file_count) -1
        assert int(walker.total_size) != int(walker4.total_size)

        # if any file is missing...

        # walker_set = set(walker.file_info.keys())
        # walker2_set = set(walker2.file_info.keys())
        # diff_set = walker2_set - walker_set
        # print (f'\nremoved file:{diff_set}')
        # print (f'source: {walker.input_source} count: {walker.file_count} size: {walker.total_size}')

        walker4 = PathWalker(self.test_folder + '/THMBNL')
        walker4.walk_path()
        walker4.get_file_md5()

        # compare MD5s and see what's missing
        print(f'walker2 hashes {walker2.file_hashes}')
        print(f'walker4 hashes {walker4.file_hashes}')

        missing_md5s = list(set(walker4.file_hashes)-set(walker2.file_hashes))
        print(missing_md5s)

        missing_value = walker2.diff_file_info(walker4,'Bytes')
        print(missing_value)

        input('PAUSED')

if __name__ == "__main__":
    unittest.main()
