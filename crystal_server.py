import collections
import gensim
import json
import os
import numpy as np
import random
import socket
import sys
import time

from model.index import Index
from utils.socket_wrapper import *
from thread import *

PREDICT_TOPICS = 'PREDICT_TOPICS'
GET_SIMILAR_REPOS_BY_LUCENE = 'GET_SIMILAR_REPOS_BY_LUCENE'
GET_SIMILAR_REPOS_BY_TFIDF = 'GET_SIMILAR_REPOS_BY_TFIDF'
GET_SIMILAR_REPOS_BY_TOPIC = 'GET_SIMILAR_REPOS_BY_TOPIC'

# Do not alter this.
HOST = ''

# Whether to use the metadata index or not.
USE_METADATA_INDEX = True

# Metadata parameters
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

# In case we did not finish labelling the topics.
JUNK_TOPIC = 'JUNK_TOPIC'
EMPTY_TOPIC = '___'

def client_thread(conn, lda_model, dictionary, label_map, \
    topic_index_root, percent_window, inverted_index, document_norms, \
    max_reply_size, tfidf_upper_threshold, id_to_link_map, num_docs, \
    metadata_index):
    """
    Function for handling connections.
    This will be used to create threads.
    """
      
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        
        #Receiving from client
        data = recv_msg(conn)
        if not data: 
            break
        
        data = json.loads(data)
        reply = []
        
        request = data[0]
        
        if request == PREDICT_TOPICS:
            print 'Requested: PREDICT_TOPICS'
            readme_text = data[1]
            percent_sum = 0.0
            unnormalized_reply = []
            for topic, percent in lda_model[dictionary.doc2bow(readme_text)]:
                topic_label = label_map[topic]
                if topic_label != JUNK_TOPIC and topic_label != EMPTY_TOPIC:
                    percent_sum += percent
                    unnormalized_reply.append( (topic_label, percent, topic) )
            # Normalize topics so they sum to 1
            for entry in unnormalized_reply:
                reply.append( (entry[0], entry[1]/percent_sum, entry[2]) )

        elif request == GET_SIMILAR_REPOS_BY_TFIDF:
            print 'Requested: GET_SIMILAR_REPOS_BY_TFIDF'
            readme_text = data[1]
            query_tokens = set(readme_text)
            
            document_scores = collections.defaultdict(float)

            for token in query_tokens:
                docs_containing_token = inverted_index[token]
                num_docs_containing_token = len(docs_containing_token)
                
                if num_docs_containing_token > tfidf_upper_threshold or num_docs_containing_token == 0:
                    continue
                    
                print '\t', token
                
                for doc_freq_pair in docs_containing_token:
                    doc_id = str(doc_freq_pair[0]) # -_- Sigh
                    doc_freq = doc_freq_pair[1]
                    document_scores[doc_id] += doc_freq
              
            for doc_id in document_scores:
                if document_norms[doc_id] != 0.0:
                    document_scores[doc_id] /= document_norms[doc_id]
                else: 
                    document_norms[doc_id] = 0.0
                    
            reply = [[k, document_scores[k]] for k in document_scores]
            reply.sort(key=lambda tup: tup[1], reverse = True)
            print '\tNumber of matches:', len(reply)
            if len(reply) > max_reply_size:
                reply = reply[:max_reply_size]
            # Sigh, the map keys are string...
            reply = [(id_to_link_map[t[0]], t[1]) for t in reply]
            
        elif request == GET_SIMILAR_REPOS_BY_TOPIC:
            print 'Requested: GET_SIMILAR_REPOS_BY_TOPIC'
            criteria = data[1]
            
            repo_ids = set()
            first = True
            
            for criterium in criteria:
                topic_id = criterium[2]
                percent = 100 * criterium[1]
            
                # Calculate which file to read.
                topic_percent = str(int(percent) / percent_window * percent_window)
                topic_percent_path = os.path.join(topic_index_root, str(topic_id), topic_percent+'.txt')

                # Our index may be incomplete.
                if not os.path.isfile(topic_percent_path):
                    print topic_percent_path, 'does not exist.'
                    continue
                    
                new_ids = set()
                for line in open(topic_percent_path):
                    new_ids.add(line.strip())
                if first:
                    repo_ids = new_ids
                    first = False
                else:
                    repo_ids.intersection_update(new_ids)
            
            # id_to_link_map is indexed by strings -_-
            reply = [id_to_link_map[i] for i in repo_ids]
            # Return a random subset.
            random.shuffle(reply)
            print '\tNumber of matches:', len(reply)
            if len(reply) > max_reply_size:
                reply = reply[:max_reply_size]

        
        elif request == GET_SIMILAR_REPOS_BY_LUCENE:
            print 'Requested: GET_SIMILAR_REPOS_BY_LUCENE'
            readme_text = data[1]
            query_tokens = set(readme_text)
            
            document_scores = collections.defaultdict(float)
            query_matches = collections.defaultdict(int)
            effective_query_tokens = 0
            
            for token in query_tokens:
                docs_containing_token = inverted_index[token]
                num_docs_containing_token = len(docs_containing_token)
                
                if num_docs_containing_token > tfidf_upper_threshold or num_docs_containing_token == 0:
                    continue
                    
                print '\t', token
                
                effective_query_tokens += 1
                idf_2 = (1 + np.log10(num_docs / (num_docs_containing_token + 1)))**2
                
                for doc_freq_pair in docs_containing_token:
                    doc_id = str(doc_freq_pair[0]) # -_- Sigh
                    doc_freq = doc_freq_pair[1]
                    document_scores[doc_id] += np.sqrt(doc_freq) * idf_2
                    query_matches[doc_id] += 1

            for doc_id in document_scores:
            
                if query_matches[doc_id] != effective_query_tokens:
                    document_scores[doc_id] *= query_matches[doc_id]
                    document_scores[doc_id] /= effective_query_tokens
                
                elif USE_METADATA_INDEX:
                    if doc_id in metadata_index:
                        doc_metadata = metadata_index[doc_id]
                        if WATCH_INDEX in doc_metadata:
                            document_scores[doc_id] *= np.log10(doc_metadata[WATCH_INDEX])
                        if STAR_INDEX in doc_metadata:
                            document_scores[doc_id] *= np.log10(doc_metadata[STAR_INDEX])
                        if CONTRIB_INDEX in doc_metadata:
                            document_scores[doc_id] *= np.log10(doc_metadata[CONTRIB_INDEX])
            
            # Sort from greatest score to least score.
            reply = [(doc_id, document_scores[doc_id]) for doc_id in document_scores]
            reply.sort(key=lambda tup: tup[1], reverse = True)
            print '\tNumber of raw matches:', len(reply)            
            
            # Remove forked projects from results.
            # Our assumption is that one repo is a fork of another if:
            # 1. They have the same repo description (raw) and repo name (derived from url).
            
            doc_norm_set = set()
            name_to_description = collections.defaultdict(set)
            
            clean_reply = []
            for t in reply:
                doc_id = t[0]
                doc_url = id_to_link_map[doc_id]
                # Name is last part of the url.
                doc_name = doc_url.split('/')[-1].lower()
                
                add_to_clean = False
                # 1
                if not add_to_clean and doc_id in metadata_index:
                    doc_metadata = metadata_index[doc_id]
                    if DESCRIPTION_INDEX in doc_metadata:
                        doc_description = doc_metadata[DESCRIPTION_INDEX]
                        if doc_description not in name_to_description[doc_name]:
                            name_to_description[doc_name].add(doc_description)
                            add_to_clean = True
                
                if add_to_clean:
                     clean_reply.append( [doc_url, document_scores[doc_id]] )
            
            reply = clean_reply
            
            print '\tNumber of de-forked matches:', len(reply)
            if len(reply) > max_reply_size:
                reply = reply[:max_reply_size]                
    
        # The API does not recognize the request.
        else:
            print 'Unknown request:', request
            
            
        reply = json.dumps(reply)
        send_msg(conn, reply)
     
    #came out of loop
    conn.close()

if __name__ == '__main__':
 
    ###
    # Parameters
    ###
 
    # Location of the gensim LDA model.
    MODEL_PATH = os.path.join('model', '106k-d_500t_100p_F-2-10', 'lda_model.mod')
    # Location of the topic labels. These must correspond to the LDA model.
    LABEL_PATH = os.path.join('model', '106k-d_500t_100p_F-2-10', 'clean_topics_106k-d_500t_100p_F-2-10.txt')
    # Location of the dictionary used to create the LDA model.
    DICTIONARY_PATH = os.path.join('model', '106k-d_500t_100p_F-2-10', 'dictionary.dict')
    # Parameters used to filter the dictionary.
    FILTER = True
    NO_BELOW = 2
    NO_ABOVE = 0.10
    # Root directory for the topic index.
    TOPIC_INDEX_ROOT = os.path.join('model', 'topic_index_10')
    # The percent window used to create the topic index.
    PERCENT_WINDOW = 10
    # Directory containing inverted index.
    INVERTED_INDEX_DIR = os.path.join('model', 'index')
    # 250 MB - The maximum cumulative file size to load into memory.
    # The actual memory consumption will be larger than this number
    # by about an order of magnitude.
    MEMORY_CACHE_LIMIT = 250e6
    # Path to the document norms.
    DOCUMENT_NORM_PATH = os.path.join('model', 'document_norms.json')
    # Id to link map
    ID_TO_LINK_MAP_PATH = os.path.join('data', 'id_to_link_map.json')
    # Path to the metadata index.
    METADATA_INDEX_PATH = os.path.join('data', 'metadata_index.json')
    
    # The maximum number of documents to return in a single reply.
    MAX_REPLY_SIZE = 25
    # Ignore terms with more than this amount of documents containing them.
    TFIDF_UPPER_THRESHOLD_SIZE = 500000 # Number of docs: 2118605
    
    NUM_DOCS = 2118605
 
    ###
    # Build TFIDF model.
    ###

    # Load the index.
    print '====='
    print 'Loading index...'
    
    t0 = time.time()
    inverted_index = Index(INVERTED_INDEX_DIR, MEMORY_CACHE_LIMIT)
    
    print 'Time to load index:', time.time() - t0
    
    # Load the document norms.
    print '====='
    print 'Loading document norms.'
    
    document_norms = json.load(open(DOCUMENT_NORM_PATH))
    
    ###
    # Load the topic-label map.
    ###
    
    print '====='
    print 'Loading topic-label map.'
    
    label_map = {}
    for line in open(LABEL_PATH):
        parts = line.strip().split(',')
        topic_id = int(parts[0])
        topic_label = parts[1].strip()
        label_map[topic_id] = topic_label
    
    ###
    # Load the id-to-link map.
    ###
    
    print '====='
    print 'Loading id-to-link map.'
    
    id_to_link_map = json.load(open(ID_TO_LINK_MAP_PATH))
    
    ###
    # Load the dictionary.
    ###

    print '====='
    print 'Loading dictionary...'

    dict_start_time = time.clock()
    dictionary = None
    if not os.path.isfile(DICTIONARY_PATH):
        print 'Cannot find dictionary:', DICTIONARY_PATH
        quit()
    dictionary = gensim.corpora.Dictionary.load(DICTIONARY_PATH)

    ###
    # Load the model.
    ###
        
    print '====='
    print 'Loading model...'
        
    lda_model = gensim.models.ldamodel.LdaModel.load(MODEL_PATH)
    
    ###
    # Filter the dictionary.
    ###

    if FILTER:
        print '====='
        print 'Filtering dictionary...'

        filter_start_time = time.clock()
        dictionary.filter_extremes(no_below=NO_BELOW, no_above=NO_ABOVE)

        print '\t', dictionary
        print '\tTime to filter:', time.clock() - filter_start_time
      
    ###
    # Load the metadata index.
    ###
    
    print '====='
    print 'Loading metadata index...'
    metadata_index = {}
    if USE_METADATA_INDEX:
        metadata_index = json.load(open(METADATA_INDEX_PATH))
      
    ###
    # Bind and listen for incoming requests.
    ###
 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created.'
     
    # Bind socket to local host and port.
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
         
    print 'Socket bind complete.'
     
    # Start listening on socket.
    s.listen(10)
    print 'Socket now listening.'

     
    # List forever.
    while 1:
        # Wait to accept a connection.
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
         
        # Start new thread to handle incoming connection.
        start_new_thread(client_thread , \
            (conn, lda_model, dictionary, \
            label_map, TOPIC_INDEX_ROOT, PERCENT_WINDOW, \
            inverted_index, document_norms, MAX_REPLY_SIZE, \
            TFIDF_UPPER_THRESHOLD_SIZE, id_to_link_map, NUM_DOCS, metadata_index))
     
    s.close()