import gensim
import json
import os
import socket
import sys
import time

from socket_wrapper import *
from thread import *

 
HOST = ''
PREDICT_TOPICS = 'PREDICT_TOPICS'
GET_SIMILAR_REPOS_BY_TFIDF = 'GET_SIMILAR_REPOS_BY_TFIDF'
GET_SIMILAR_REPOS_BY_TOPIC = 'GET_SIMILAR_REPOS_BY_TOPIC'

def client_thread(conn, lda_model, dictionary, label_map, \
    topic_index_root, percent_window):
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
            print GET_SIMILAR_REPOS_BY_TFIDF, 'is not implemented.'
            
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
                print topic_percent_path
                # Our index may be incomplete.
                if not os.path.isfile(topic_percent_path):
                    print topic_percent_path, 'does not exist.'
                    continue
                    
                new_ids = set()
                for line in open(topic_percent_path):
                    new_ids.add(int(line.strip()))
                if first:
                    repo_ids = new_ids
                    first = False
                else:
                    repo_ids.intersection_update(new_ids)
            reply = list(repo_ids)
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
    TOPIC_INDEX_ROOT = os.path.join('model', 'topic_index_5')
    # The percent window used to create the topic index.
    PERCENT_WINDOW = 5
 
    # TODO Build TFIDF model. 
    #quit()
    
    # TODO Load the topic-label map.
    label_map = {}
    for line in open(LABEL_PATH):
        parts = line.strip().split(',')
        topic_id = int(parts[0])
        topic_label = parts[1].strip()
        label_map[topic_id] = topic_label
    
    ###
    # Load the dictionary.
    ###

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
            label_map, TOPIC_INDEX_ROOT, PERCENT_WINDOW))
     
    s.close()