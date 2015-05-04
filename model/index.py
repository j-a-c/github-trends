import collections
import numpy as np
import json
import os
import time
import xxhash

class Index(object):
    """
    Class acting as an abstraction for the inverted index.
    """
    
    def __init__(self, index_dir, cache_memory_limit):
        """
        Arguments:
            index_dir - The top level directory containing the index.
            cache_memory_limit - The memory limit (in bytes) for the in-memory
                index cache.

        Returns:
            Nothing
        """
        self.index_dir = index_dir
        self.index_ending = '_inverted_index.json'

        self.num_index_files = 10000

        self.cache_contents = set()
        self.index_cache = collections.defaultdict(list)

        self.lru = None
        self.lru_hash = None

        if cache_memory_limit:
            paths = [os.path.join(index_dir,p) for p in os.listdir(index_dir)]
            paths.sort(key=lambda p: os.path.getsize(p), reverse=True)

            total_size = 0
            for path in paths:
                file_size = os.path.getsize(path)
                if total_size + file_size > cache_memory_limit:
                    break
                total_size += file_size

                temp_index = json.load(open(path))
                for key in temp_index:
                    self.index_cache[key] = temp_index[key]
                self.cache_contents.add(self.get_hash_from_filename(path))

            print 'Number of indexes loaded:', len(self.cache_contents)
            print 'Cache size:', total_size
        
    def get_hash_from_filename(self, filename):
        """
        Arguments:
            filename - The name (can include the path to the file) of a file to
                retrieve the has key from.

        Returns:
            The hash key for all tokens that mapped to that index.
        """
        filename_only = filename.split(os.path.sep)[-1]
        return int(filename_only.split('_')[0])

    def index_hash(self, token):
        """
        Arguments:
            token - The token to compute the hash for.
            
        Returns:
            The hash of the token, which can be used to map the token to an
            index file.
        """
        x = xxhash.xxh64()
        x.update(token)
        return x.intdigest() % self.num_index_files

    def get_index_name(self, token):
        """
        Arguments:
            token - The token to find an index file for.
            
        Returns:
            Returns the filename for the index that the token hashes to.
        """
        break_index = self.index_hash(token)
        index_name =  str(break_index) + self.index_ending
        return os.path.join(self.index_dir, index_name)

    def __getitem__(self, token):
        """
        See get().
        """
        return self.get(token)
        
    def get(self, token, cache=True):
        """
        Arguments:
            token - a token to query the inverted index for.

        Returns:
            The inverted index entry for that token, or an empty list of one
            does not exist.
        """
        try:
            token_hash = self.index_hash(token)
        except:
            return []
        
        if token_hash in self.cache_contents:
            return self.fix_bug(self.index_cache[token])
        elif self.lru and token_hash == self.lru_hash:
            if token in self.lru:
                return self.fix_bug(self.lru[token])
            else: return []
        else:
            temp_path = self.get_index_name(token)

            if not os.path.isfile(temp_path):
                return []
            
            lru = json.load(open(temp_path))
            lru_hash = self.get_hash_from_filename(temp_path)

            if cache:
                self.lru = lru
                self.lru_hash = lru_hash
            
            if token in lru:
                return self.fix_bug(lru[token])
            else: return []

    def fix_bug(self, entry):
        """
        We need to use this method due to a bug in the build index code.
        The index code is fixed, but we will need to rebuild the index before
        removing this code.
        """
        if len(entry) > 0:
            new_entry = entry[0]
            new_entry.extend(entry[1:])
            return new_entry
        return []

    def __iter__(self):
        """
        Arguments:
            None

        Returns:
            An iterator over the keys of the inverted index.
        """
        return IndexIterator(self)

    def size(self):
        counter = 0
        for f in os.listdir(index.index_dir):
            next_index_path = os.path.join(index.index_dir, f)
            next_index = json.load(open(next_index_path))
            counter += len(next_index)
        return counter

class IndexIterator(object):
    """
    Iterates over the keys of the inverted index.
    """

    def __init__(self, index):
        self.index = index
        self.files = os.listdir(index.index_dir)
        self.file_index = -1
        self.key_index = -1
        self.keys = None

    def _load_next_index(self):
        self.file_index += 1

        if not self.file_index < len(self.files):
            raise StopIteration

        next_index_path = os.path.join(self.index.index_dir, self.files[self.file_index])
        self.keys = json.load(open(next_index_path)).keys() 
        self.key_index = 1
        return self.keys[self.key_index-1]

    def next(self):
        if not self.keys:
            return self._load_next_index()
        else:
            if self.key_index < len(self.keys):
                self.key_index += 1
                return self.keys[self.key_index-1]
            else:
                return self._load_next_index()

if __name__ == '__main__':

    # Directory containing index.
    index_dir = 'index'
    # 250 MB
    memory_cache_limit = 250e6

    # Load the index.
    print 'Loading index...'
    t0 = time.time()
    index = Index(index_dir, memory_cache_limit)
    print 'Time to load index:', time.time() - t0

    print 'Index loaded.'

    # Accessing an entry in the index.
    t0 = time.time()
    print len(index.get('grit'))
    print len(index.get('a'))
    print len(index.get('linux'))
    print len(index.get('zebra'))
    print len(index.get('destroyaliens'))
    print 'Time to query:', time.time() - t0

    # Calculate document norms.
    
    CLEAN_README_ROOT = os.path.join('..', 'data', 'clean')
    
    print 'Counting the number of documents.'
    n_docs = 0
    for d in os.listdir(CLEAN_README_ROOT):
        n_docs += len(os.listdir(os.path.join(CLEAN_README_ROOT, d)))
    
    print 'Number of docs:', n_docs
    
    norms = collections.defaultdict(float)
    
    print 'Iterating over terms.'
    current_term = 0
    for term in index:
        term_idf = np.log(n_docs / (1.0+len(index[term])))
        
        for doc_freq_pair in index[term]:
            doc_id = doc_freq_pair[0]
            doc_freq = doc_freq_pair[1]
            
            norms[doc_id] += (doc_freq * term_idf)**2
            
        current_term += 1
        if current_term % 10000 == 0:
            print 'Terms processed:', current_term
    print 'Terms processed:', current_term
           
    print 'Calculating roots.'
    for k in norms:
        norms[k] = np.sqrt(norms[k])
    
    print 'Number of keys in norms:', len(norms)
    
    json.dump(norms, open('document_norms.json', 'w+'))
    
    quit()

    '''
    # Iterating over the keys in the index.
    for key in index:
        try:
            print key.decode('utf-8')
        except:
            pass
    '''

    '''
    # 3012280, takes a while to read all the files
    print 'Number of tokens in index:', index.size()
    '''
