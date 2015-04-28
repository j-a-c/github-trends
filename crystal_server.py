import collections
import gensim
import json
import os
import random
import socket
import sys
import time

from model.index import Index
from utils.socket_wrapper import *
from thread import *

 
HOST = ''
PREDICT_TOPICS = 'PREDICT_TOPICS'
GET_SIMILAR_REPOS_BY_TFIDF = 'GET_SIMILAR_REPOS_BY_TFIDF'
GET_SIMILAR_REPOS_BY_TOPIC = 'GET_SIMILAR_REPOS_BY_TOPIC'

def client_thread(conn, lda_model, dictionary, label_map, \
    topic_index_root, percent_window, inverted_index, document_norms, \
    max_reply_size, tfidf_upper_threshold, id_to_link_map):
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
            readme_text = data[1]
            for topic, percent in lda_model[dictionary.doc2bow(readme_text)]:
                topic_label = label_map[topic]
                reply.append( (topic_label, percent, topic) )

        elif request == GET_SIMILAR_REPOS_BY_TFIDF:
            readme_text = data[1]
            query_tokens = set(readme_text)
            
            document_scores = collections.defaultdict(float)
            
            for token in query_tokens:
                docs_containing_token = inverted_index[token]
                if len(docs_containing_token) > tfidf_upper_threshold:
                    continue
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
            if len(reply) > max_reply_size:
                reply = reply[:max_reply_size]
            # Sigh, the map keys are string...
            reply = [id_to_link_map[t[0]] for t in reply if t[0] in id_to_link_map]
            
        elif request == GET_SIMILAR_REPOS_BY_TOPIC:
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
            reply = [id_to_link_map[i] for i in repo_ids if i in id_to_link_map]
            # Return a random subset.
            random.shuffle(reply)
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
    
    # The maximum number of documents to return in a single reply.
    MAX_REPLY_SIZE = 25
    # Ignore terms with more than this amount of documents containing them.
    TFIDF_UPPER_THRESHOLD_SIZE = 500000 # Number of docs: 2118605
 
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
            TFIDF_UPPER_THRESHOLD_SIZE, id_to_link_map))
     
    s.close()