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
    
    README_INDEX_LIST_FILE = 'clean_readme_index_list.json'
    METADATA_DIRECTORY = 'metadata'
    
    # Get README index.
    all_readmes = json.load(open(README_INDEX_LIST_FILE))

    readme_index = 0

    for meta_file in sorted(os.listdir(METADATA_DIRECTORY), key = lambda p: int(p.split('.')[0])):
        meta_file_path = os.path.join(METADATA_DIRECTORY, meta_file)
        with open(meta_file_path, 'r') as current_meta_file:
            reader = csv.reader(current_meta_file, delimiter=',', quotechar='"')

            for row in reader:
                # We are missing this README.
                current_row = int(row[README_ID_INDEX])
                if all_readmes[readme_index] > current_row:
                    # We do not have this README on disk.
                    pass
                elif all_readmes[readme_index] < current_row:
                    print 'Missing README:', all_readmes[readme_index]
                    if readme_index + 1 >= len(all_readmes):
                        quit()
                    while all_readmes[readme_index+1] < current_row:
                        readme_index += 1
                        print 'Missing README:', all_readmes[readme_index]
                    readme_index += 1
                else: # Validate fields.
                    readme_index += 1

                 if readme_index + 1 == len(all_readmes) : quit()
