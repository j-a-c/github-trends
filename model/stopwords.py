import heapq
import json
import os

from index import Index
from numpy import log as ln

def predict_stopwords(inv_idx, num_docs, output_file):
    """
    Arguments:
        inv_idx: The inverted index for the corpus.
        num_docs: The number of documents in the corpus.

    Returns:
        stopwords: A JSON-serialized string for an array of words.
    """
    NUM_KEEP_THRESHOLD = 10000

    num_tokens_processed = 0
    
    # Calculate normalized IDF and the entropy of each word.
    nidf_heap = []
    entropies_heap = []
    
    for token in inv_idx:

        token_entry = inv_idx.get(token) 
        
        # NIDF
        N = num_docs       
        Dk = len(token_entry)
        # Negate the NIDF since we are keeping a min heap.
        nidf = -(N - Dk + 0.5)/(Dk + 0.5)
        # Attempt to add to heap.
        if len(nidf_heap) < NUM_KEEP_THRESHOLD:
            heapq.heappush(nidf_heap, (nidf,token) )
        elif nidf < heap[0][0]:
            heapq.heappushpop(nidf_heap, (nidf,token))

        # Entropy
        token_total = sum(t[1] for t in token_entry)
        entropy = 0.0
        for t in token_entry:
            prob_token = 1.0*t[1] / token_total
            entropy += prob_token * ln(prob_token)      
        entropy /= num_docs
        entropy += 1
        # Negate the entropy since we are keeping a min heap.
        entropy *= -1
        # Attempt to add to heap.
        if len(entropies_heap) < NUM_KEEP_THRESHOLD:
            heapq.heappush(entropies_heap, (entropy,token) )
        elif entropy < heap[0][0]:
            heapq.heappushpop(entropies_heap, (entropy,token))
            
        num_tokens_processed += 1
        if num_tokens_processed % 1000 == 0:
            print 'Number of tokens processed:', num_tokens_processed

    # Write lists to disk.
    json.dump(nidf_heap, open('nidf_' + output_file, 'w+'))
    json.dump(entropies_heap, open('entropy_' + output_file, 'w+'))

if __name__ == '__main__':
    output_file = 'stopwords.json'
    
    index_dir = 'index'
    # 10 MB
    memory_cache_limit = 10e6

    print 'Building index.'
    index = Index(index_dir, memory_cache_limit)
    
    print 'Counting READMEs'
    # 2118605
    clean_readme_path = os.path.join('..', 'data', 'clean')
    num_docs = 2118605
    #num_docs = sum([len(os.listdir(os.path.join(clean_readme_path,d))) for d in os.listdir(clean_readme_path)])
    
    print 'Number of cleaned READMEs:', num_docs
    
    print 'Predicting stopwords'
    predict_stopwords(index, num_docs , output_file)
