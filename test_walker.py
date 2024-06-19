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
        print (f'\nsource: {walker.input_source}\ncount: {walker.file_count}\nsize: {walker.total_size}')
        dumped_csv_fpath = walker.dump_csv() # dump it

        # Create Walker from resulting csv
        walker2 = PathWalker(dumped_csv_fpath) #set walker to a csv
        walker2.read_csv_special() # read contents in
        print (f'\nsource: {walker2.input_source}\ncount: {walker2.file_count}\nsize: {walker2.total_size}')

        # Make sure the count and size is the same
        assert int(walker.file_count) == int(walker2.file_count)
        assert int(walker.total_size) == int(walker2.total_size)

        #remove file and recreate walker object
        first_file = list(walker.file_info.keys())[1]
        first_file_path = walker.file_info[first_file]['File Path']
        os.remove(first_file_path)
        walker = PathWalker(self.test_folder+'/THMBNL') #set walker to a directory
        walker.walk_path() # walk it

        # Make sure the count and size is the same
        assert int(walker.file_count) == int(walker2.file_count) - 1
        assert int(walker.total_size) != int(walker2.total_size)

        # here is how to check which file is missing
        walker_set = set(walker.file_info.keys())
        walker2_set = set(walker2.file_info.keys())
        diff_set = walker2_set - walker_set
        print (f'\nremoved file:{diff_set}')
        print (f'\nsource: {walker.input_source}\ncount: {walker.file_count}\nsize: {walker.total_size}')



        # input('PAUSED')

if __name__ == "__main__":
    unittest.main()
