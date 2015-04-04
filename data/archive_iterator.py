import os
import shutil

class ArchiveIterator():
    def __init__(self, paths):
        self.paths = paths
        self.current_path_index = 0
        self.current_line_index = -1
        self.current_file_index = -1
        self.current_lines = None
        self.current_files = None
        self.TEMP_DIR = 'TEMP_ARCHIVE_ITERATOR_DIR'

        # Clean up, if necessary.
        if os.path.exists(self.TEMP_DIR):
           shutil.rmtree(self.TEMP_DIR)    

    
    def __iter__(self):
        return self


    def next(self):
        # We need to try to extract next file
        if not self.current_lines:
            # Delete previous archive extraction.
            if os.path.exists(self.TEMP_DIR):
                shutil.rmtree(self.TEMP_DIR)                
            os.mkdir(self.TEMP_DIR)


            # Extract next archive.
            if self.current_path_index < len(self.paths):
                command = '7z e -o' + self.TEMP_DIR + ' ' + self.paths[self.current_path_index]
                self.current_path_index += 1
                os.system(command)
                print command
            # No more files to extract.
            else:
                if os.path.exists(self.TEMP_DIR):
                    shutil.rmtree(self.TEMP_DIR) 
                raise StopIteration

            # Get and sort the current extracted files.
            self.current_files = [os.path.join(self.TEMP_DIR,f) for f in os.listdir(self.TEMP_DIR)]
            # Sort by int(filename)
            self.current_files.sort(key=lambda f: int(f.split(os.path.sep)[-1].split('.')[0]))

            self.current_file_index = 0
            self.current_lines = open(self.current_files[self.current_file_index]).readlines()
            self.current_line_index = 1
            return self.current_lines[self.current_line_index - 1]

        else:
            self.current_line_index += 1
            line_to_return = self.current_lines[self.current_line_index - 1]

            # We are out of lines, try open the next file.
            if self.current_line_index >= len(self.current_lines):
                self.current_file_index += 1
                # There is another file from the current archive.
                if self.current_file_index < len(self.current_files):
                    current_file = self.current_files[self.current_file_index]
                    self.current_lines = open(current_file).readlines()
                    self.current_line_index = 0
                # We need to extract the next archive, so we will indicate this.
                else:
                    self.current_lines = None

            return line_to_return
