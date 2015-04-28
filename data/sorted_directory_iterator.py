import json
import os

class SortedDirectoryIterator(object):
    def __init__(self, d):
        self.files = [os.path.join(d,p) for p in os.listdir(d)]
        self.files.sort(key = lambda p: int(p.split(os.path.sep)[-1].split('.')[0]))

        self.lines = None
        self.current_file_index = -1
        self.current_line_index = -1
        
    def __iter__(self):
        self.lines = None
        self.current_file_index = -1
        self.current_line_index = -1
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


if __name__ == '__main__':
    target = 11333473

    print 'Creating iterator.'
    iterator = SortedDirectoryIterator(os.path.join('..', 'urls', 'raw'))
    
    README_INDEX_LIST_FILE = 'clean_readme_index_list.json'
    all_readmes = json.load(open(README_INDEX_LIST_FILE))
    print len(all_readmes)

    counter = 0
    readme_index = 0

    id_to_link_map = {}
    for url in iterator:
        # Only process a URL that is in our README list.
        try:
            if all_readmes[readme_index] == counter:
                readme_index += 1

                id_to_link_map[counter] = url
            counter += 1
        except:
            break
        
    json.dump(id_to_link_map, open('id_to_link_map.json', 'w+'))
    
    print 'Number of links:', len(id_to_link_map)    
    print id_to_link_map[11333473]
    
            
            
            
