import json
import os

"""
Builds a JSON array containing the indices that have been samples.
"""
if __name__ == '__main__':
    README_DIR = 'clean'
    OUTPUT_FILE = 'clean_readme_index_list.json'
    
    all_readmes = []

    # Looping manually is faster because we do not need to do lots of isFile()
    # checks.
    print 'Finding READMEs.'
    for d in os.listdir(README_DIR):
        for p in os.listdir(os.path.join(README_DIR, d)):
            all_readmes.append(int(p.split(os.path.sep)[-1].split('.')[0]))

    print 'Sorting.'
    all_readmes.sort()

    print 'Dumping json.'
    json.dump(all_readmes, open(OUTPUT_FILE, 'w+'))

    print 'Number of READMEs:', len(all_readmes)
