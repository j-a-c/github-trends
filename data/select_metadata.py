import csv
import json
import os

README_ID_INDEX = '0'
WATCH_INDEX = '1'
STAR_INDEX = '2'
FORK_INDEX = '3'
COMMIT_INDEX = '4'
BRANCH_INDEX = '5'
RELEASES_INDEX = '6'
CONTRIB_INDEX = '7'
LATEST_AUTHOR_INDEX = '8'
DESCRIPTION_INDEX = '9'
LATEST_README_INDEX = '10'
FIRST_README_INDEX = '11'

if __name__ == '__main__':
    
    METADATA_DIRECTORY = 'metadata'
   
    f = open('selected_metadata.txt', 'w+')

    num_found = 0
    
    for meta_file in sorted(os.listdir(METADATA_DIRECTORY), key = lambda p: int(p.split('.')[0])):
        meta_file_path = os.path.join(METADATA_DIRECTORY, meta_file)
        print meta_file_path
        with open(meta_file_path, 'r') as current_meta_file:
            reader = csv.reader(current_meta_file, delimiter=',', quotechar='"')

            for row in reader:
                row = row
                if len(row)  < 5:
                    continue
                
                if len(row[-1]) > 1 and len(row[-2]) > 1 and len(row[-4]) > 10:
                    f.write(row[0] + ' ' + row[-1] + ' ' + row[-2] + ' ' + row[-4] + '\n')
                    num_found += 1
    f.close()
    
    print 'Number found:', num_found
                