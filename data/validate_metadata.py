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
   
    readme_index = 0
    
    missing_fields = collections.defaultdict(int)
    
    fields = [str(i) for i in range(12)]

    print 'Loading metadata...'
    metadata_index = json.load(open('metadata_index.json'))
    print 'Metadata loaded.'

    counter = 0
    for entry in metadata_index:
        counter += 1
        for field in fields:
            if field not in entry:
                missing_fields[field] += 1
                
        if counter % 10000 == 0:
            print counter

    for k in missing_fields:
        print k, missing_fields[k]