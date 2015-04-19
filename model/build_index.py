import bisect
import collections
from index import Index
import json
import os
import xxhash

def dump_to_disk(temp_index, index):
    current_index = None
    current_index_name = None

    # Sort tokens so we don't have to re-read the same file too many times.
    print '\tSorting index keys...', len(temp_index)
    tokens_processed = 0
    sorted_keys = sorted(temp_index.keys(), key=lambda t : index.index_hash(t))
    for token in sorted_keys:
        next_index_name = index.get_index_name(token)
        if next_index_name == current_index_name:
            if token in current_index:
                current_index[token].extend(temp_index[token])
            else:
                current_index[token] = [temp_index[token]]
        else:
            # Save previous work
            if current_index:
                json.dump(current_index, open(current_index_name, 'w+'))

            # Load new work
            if os.path.isfile(next_index_name):
                current_index = json.load(open(next_index_name))
            else:
                current_index = collections.defaultdict(list)
            current_index_name = next_index_name

            if token in current_index:
                current_index[token].extend(temp_index[token])
            else:
                current_index[token] = [temp_index[token]]

        tokens_processed += 1
        if tokens_processed % 1000 == 0:
            print '\tNumber of tokens processed:', tokens_processed

    # Don't forget to dump the very last token group.
    if current_index:
        json.dump(current_index, open(current_index_name, 'w+'))
        

if __name__ == '__main__':

    FILES_PER_DUMP = 500000
    CLEAN_DIR = os.path.join('..', 'data', 'clean')

    num_readmes_processed = 0
    temp_index = collections.defaultdict(list)
    index = Index('index', None)

    print 'Starting to build index...'
    for d in os.listdir(CLEAN_DIR):
        for f in os.listdir(os.path.join(CLEAN_DIR, d)):
            readme_lines = open(os.path.join(CLEAN_DIR,d,f), 'r').readlines()
            readme_tokens = ' '.join(readme_lines)
            readme_tokens = readme_tokens.split()

            if len(readme_tokens) == 0:
                continue

            repo_num = int(f.split('.')[0])

            counter = 0
            
            readme_tokens.sort()
            previous_token = readme_tokens[0]
            
            for token in readme_tokens:
                
                if token == previous_token:
                    counter += 1
                else:
                    temp_index[previous_token].append( (repo_num, counter) )
                    previous_token = token
                    counter = 1

            # Add the last token group
            temp_index[previous_token].append( (repo_num, counter) )
            
            num_readmes_processed += 1
            if num_readmes_processed % FILES_PER_DUMP == 0:
		print 'Dumping to disk...'
                dump_to_disk(temp_index, index)
                temp_index = None
                temp_index = collections.defaultdict(list)
                print 'Number of READMEs processed', num_readmes_processed

    # Whatever is left.
    dump_to_disk(temp_index, index)
    print 'Number of READMEs processed', num_readmes_processed
    
