import collections
import csv
import json
import os

# The feature indices.
README_ID_INDEX = 0
WATCH_INDEX = 1
STAR_INDEX = 2
FORK_INDEX = 3
COMMIT_INDEX = 4
BRANCH_INDEX = 5
RELEASES_INDEX = 6
CONTRIB_INDEX = 7
LATEST_AUTHOR_INDEX = 8
DESCRIPTION_INDEX = 9,
LATEST_README_INDEX = 10,
FIRST_README_INDEX = 11

if __name__ == '__main__':
    
    METADATA_DIRECTORY = 'metadata'
   
    metadata_index = collections.defaultdict(lambda: {})

    for meta_file in sorted(os.listdir(METADATA_DIRECTORY), key = lambda p: int(p.split('.')[0])):
        meta_file_path = os.path.join(METADATA_DIRECTORY, meta_file)
        print meta_file_path
        with open(meta_file_path, 'r') as current_meta_file:
            reader = csv.reader(current_meta_file, delimiter=',', quotechar='"')

            for row in reader:
                if len(row) == 1:
                    metadata_index[row[0]] = {}
                else:
                    for e,i in enumerate(row):
                        if i != '_' and e != 0:
                            if e >= 1 and e <= 7:
                                if i.endswith('+'):
                                    i = i[:-1]
                                i = int(i.replace(',', ''))
                                if i > 10: # To keep the entries relatively sparse.
                                    metadata_index[row[0]][e] = i
                            else:
                                metadata_index[row[0]][e] = i
                            
    json.dump(metadata_index, open('metadata_index.json', 'w+'))