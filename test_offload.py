import unittest
import shutil
import os
from walker import AutoWalker
import offloader

class TestWalker(unittest.TestCase):

    def setUp(self):

        # Set up thumbnail photos
        self.test_folder = 'tests/dev-TempDirectory'
        self.thumbs = os.path.join(self.test_folder,'Thumbs')
        shutil.copytree('tests/fixtures/THMBNL',self.thumbs)

        # Define the names of the subfolders for recursive testing
        subfolders = ['subfolder1', 'subfolder2', 'subfolder3']

        # Create a parent directory (if it doesn't exist)
        self.parent_directory = os.path.join(self.test_folder,'parent_folder')
        os.makedirs(self.parent_directory, exist_ok=True)

        # Define the path for the empty text file
        file_path = os.path.join(self.parent_directory, 'empty_parent_file.txt')
        
        # Create the empty text file
        with open(file_path, 'w') as file:
            pass

        # Loop through the list of subfolders
        for subfolder in subfolders:
            # Create the subfolder path
            subfolder_path = os.path.join(self.parent_directory, subfolder)
            
            # Create the subfolder (if it doesn't exist)
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Define the path for the empty text file
            file_path = os.path.join(subfolder_path, f'empty_file_{subfolder}.txt')
            
            # Create the empty text file
            with open(file_path, 'w') as file:
                pass

# print("Empty text files have been created in each subfolder.")





                        
    def tearDown(self):
        # Clean up temporary folders after testing
        shutil.rmtree(self.test_folder)

    def test_01_sync_top_level_files(self):
        '''
        test sync
        '''
        top_level_files_folder = os.path.join(self.test_folder,'test_01_sync_top_level_files')
        os.makedirs(top_level_files_folder)
        offloader.sync_top_level_files(self.parent_directory, top_level_files_folder)
        # input('PAUSED.. hit return to continue')

    def test_02_recursive_sync(self):
        '''
        test sync recursive 02
        '''
        subfolders_dir = os.path.join(self.test_folder,'test_02_recursive_sync')
        os.makedirs(subfolders_dir)
        offloader.sync_subfolders(self.parent_directory, subfolders_dir)
        # input('PAUSED.. hit return to continue')

    def test_03_dated_photo_sync(self):
        '''
        sync photos in dated pattern
        '''
        subfolders_dir = os.path.join(self.test_folder,'test_03_dated_photo_sync')
        os.makedirs(subfolders_dir)
        offloader.rsync_dated_photos(self.thumbs, subfolders_dir)

        # Do it again to see if the files are skipped
        offloader.rsync_dated_photos(self.thumbs, subfolders_dir)

        # Make sidecar and read out contents
        offloader.gen_sidecars_recursive(subfolders_dir)
        sidecar_contents = offloader.read_sidecars_recursive(subfolders_dir)
        print('**************************************')

        input('PAUSED.. hit return to continue')


    def test_04_sync_flat_dates(self):
        '''
        test sync dated files in a flat way
        '''
        subdir = os.path.join(self.test_folder,'test_04_sync_flat_dates')
        os.makedirs(subdir)
        # offloader.rsync_flat_dates(self.thumbs, subdir)
        offloader.walk_scr_and_copy_all_media_to_dst_in_flat_dated_format(self.thumbs, subdir)
        input('PAUSED.. hit return to continue')
        # Make sidecars:
        for dirname in [subdir, self.thumbs]:
            offloader.gen_sidecars_recursive(dirname)
            # for fname in os.listdir(dirname):
            #     fpath = os.path.join(dirname,fname)
            #     src_md5 = offloader.calculate_md5(fpath)
            #     sidecar_path = offloader.create_sidecar_file(fpath, src_md5)
            #     side_md5 = offloader.read_sidecar_file(sidecar_path)
            #     print(src_md5, side_md5)
        input('PAUSED.. hit return to continue')

    def test_print_totals(self):
        '''
        test walker
        '''
        # walker = AutoWalker(self.test_folder)
        # print (f'\nsource: {walker.source_path}\ncount: {walker.file_count}\nsize: {walker.total_size}')
        pass

if __name__ == "__main__":
    unittest.main()
