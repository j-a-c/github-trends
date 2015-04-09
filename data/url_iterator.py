import os

class URLIterator(object):
    def __init__(self, d):
        self.files = [os.path.join(d,p) for p in os.listdir(d)]
        self.files.sort(key = lambda p: int(p.split(os.path.sep)[-1].split('.')[0]))
        self.lines = None

        self.current_file_index = -1
        self.current_line_index = -1

    def __iter__(self):
        return self

    def _get_line_from_next_file(self):
            self.current_file_index += 1

            if not self.current_file_index < len(self.files):
                raise StopIteration

            self.lines = open(self.files[self.current_file_index]).readlines()
            self.current_line_index = 1

            return self.lines[self.current_line_index-1].strip()

    def next(self):
        if not self.lines:
            return self._get_line_from_next_file()
        else:
            if self.current_line_index < len(self.lines):
                self.current_line_index += 1
                return self.lines[self.current_line_index-1].strip()
            else:
                return self._get_line_from_next_file()
            
            
            
