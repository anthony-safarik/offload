from walker import FileWalker
import sys

if __name__ == "__main__":

    check_file_hashes = False

    if len(sys.argv) > 1:
        source_directory = sys.argv[1]
    else:
        source_directory = input("Enter the source path: ")

    if len(sys.argv) > 2:
        compare_directory = sys.argv[2]
    else:
        compare_directory = input("Enter the compare path: ")

    if len(sys.argv) > 3:
        check_file_hashes = True
    else:
        check_file_hashes = input(f"Check MD5 file hashes? (y/n): ").lower() == "y"






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

    if check_file_hashes:
        walker.get_file_md5()
        walker2.get_file_md5()
        print (f'MD5 that do not match:\n{walker.md5_unequal(walker2)}\n')

    dicts_for_csv = list(walker.file_info.values())
    dicts_for_csv2 = list(walker2.file_info.values())
    walker.write_dicts_to_csv(dicts_for_csv, str(walker.source_path)+'_FILE_INFO.csv')
    walker.write_dicts_to_csv(dicts_for_csv2, str(walker2.source_path)+'_FILE_INFO.csv')