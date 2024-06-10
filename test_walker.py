import unittest
import shutil
import os
from walker import AutoWalker

class TestWalker(unittest.TestCase):

    def setUp(self):
        # Create temporary folders for testing
        self.test_folder = "tests/dev-test_folder"

        os.makedirs(self.test_folder, exist_ok=True)


        #Copy temporary files for testing
        self.thm = os.path.join(os.getcwd(),'tests/fixtures/THMBNL')
        self.thm = 'tests/fixtures/THMBNL'
        shutil.copytree(self.thm,os.path.join(self.test_folder,'THMBNL'))
                        
    def tearDown(self):
        # Clean up temporary folders after testing
        shutil.rmtree(self.test_folder)

    # def test_pause(self):
    #     '''
    #     test pause
    #     '''
    #     input('PAUSED.. hit return to continue')

    def test_pause(self):
        '''
        test walker
        '''
        walker = AutoWalker(self.test_folder)
        print (f'\nsource: {walker.source_path}\ncount: {walker.file_count}\nsize: {walker.total_size}')

if __name__ == "__main__":
    unittest.main()
