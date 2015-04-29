import gensim
import json
import socket
import struct
import time
 
from crystal_server import GET_SIMILAR_REPOS_BY_LUCENE, GET_SIMILAR_REPOS_BY_TFIDF, GET_SIMILAR_REPOS_BY_TOPIC, PREDICT_TOPICS
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from utils.socket_wrapper import *

class GithubCrystalApi(object):

    def __init__(self):
        HOST = 'localhost'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def predict_topics(self, readme_tokens):
        """
        Returns a list of (topic name, percentage tuples) for the readme_tokens.
        """
        
        send_msg(self.s, json.dumps([PREDICT_TOPICS,readme_tokens]))
        return json.loads(recv_msg(self.s))
      
    def get_similar_repos_by_lucene(self, readme_tokens):
        send_msg(self.s, json.dumps([GET_SIMILAR_REPOS_BY_LUCENE, readme_tokens]))
        return json.loads(recv_msg(self.s))
      
    def get_similar_repos_by_topic(self, criteria):
        """
        Returns a list of repository IDs that have topic compositions
        within +/- the topic index's percentage. The percentage depends on the
        index used by the index server.
        
        Criteria must be in form [(topid_id, percent)+].
        """
        send_msg(self.s, json.dumps([GET_SIMILAR_REPOS_BY_TOPIC, criteria]))
        return json.loads(recv_msg(self.s))
        
    def get_similar_repos_by_tfidf(self, readme_tokens):
        send_msg(self.s, json.dumps([GET_SIMILAR_REPOS_BY_TFIDF, readme_tokens]))
        return json.loads(recv_msg(self.s))
 
 
 
def tokenize(text):
    return [token for token in gensim.utils.simple_preprocess(text) if token not in gensim.parsing.preprocessing.STOPWORDS]
 
if __name__ == '__main__':
    api = GithubCrystalApi()
    
    readme = 'clone of the operating system Unix'
    readme_tokens = tokenize(readme)
    
    """ How to predict topics. """
    t0 = time.clock()
    
    topics = api.predict_topics(readme_tokens)
    
    print 'Time for topic prediction query:', time.clock() - t0
    
    print 'Topics'
    for topic_label, percent, topic_id in topics:
        print '\t', topic_label, percent
    
    """ How to get similar repositories by topic. """
    
    # One topics.
    # Note that we have to wrap a single topic in [] since the API expects a list.
    t0 = time.clock()
    
    similar_topic_repos = api.get_similar_repos_by_topic([topics[0]])
    
    print 'Time for similar topics query:', time.clock() - t0
    
    print 'Number of repos close to', topics[0][1], 'of', \
        topics[0][0], ':', len(similar_topic_repos)
    
    for s in similar_topic_repos:
        print '\t', s
        
    # Multiple topics.
    if len(topics) > 1:
        t0 = time.clock()
        
        similar_topic_repos = api.get_similar_repos_by_topic(topics[:2])
        
        print 'Time for topic similarity query:', time.clock() - t0
        
        print 'Number of repos close to', topics[0][1], 'of', \
            topics[0][0], 'and', topics[1][1], 'of', \
            topics[1][0], ':', len(similar_topic_repos)
        
        for s in similar_topic_repos:
            print '\t', s
        
    """ How to get similar repositories by TFIDF. """
    
    t0 = time.clock()
    
    similar_docs = api.get_similar_repos_by_tfidf(readme_tokens)
    
    print 'Time for TFIDF query:', time.clock() - t0
    for s in similar_docs:
        print '\t', s
     
     
    """ How to get similar repositories by Lucene's criteria. """
    
    t0 = time.clock()
    
    similar_docs = api.get_similar_repos_by_lucene(readme_tokens)
    
    print 'Time for Lucene query:', time.clock() - t0
    for s in similar_docs:
        print '\t', s