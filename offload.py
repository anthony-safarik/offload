from pathlib import Path
import os

class FileWalker:
    def __init__(self, source_path):
        self.source_path = Path(source_path)
        self.file_paths = {}

    def walk_directory(self):
        for root, dirs, files in os.walk(self.source_path):
            for file_name in files:
                file_path = Path(root) / file_name
                # self.file_paths[str(file_path)] = file_path
                self.file_paths[str(file_path.relative_to(self.source_path))] = file_path

    def print_file_paths(self):
        for file_path in self.file_paths.values():
            print(f'{file_path.relative_to(self.source_path)} --- {file_path.stat()}')

    def compare_files(self, other):
        return sorted(self.file_paths.keys()) == sorted(other.file_paths.keys())
    
    def minus(self, other):
        return [x for x in self.file_paths.keys() if x not in other.file_paths.keys()]

# Example usage
if __name__ == "__main__":
    source_directory = input("Enter the source path: ")
    walker = FileWalker(source_directory)
    walker.walk_directory()

#compare_files 
    compare_directory = input("Enter the compare path: ")
    walker2 = FileWalker(compare_directory)
    walker2.walk_directory()

    print(walker.minus(walker2))
    print(walker2.minus(walker))
    print (walker.compare_files(walker2))

    # walker.print_file_paths()