import json
import socket
import struct
 
from crystal_server import GET_SIMILAR_REPOS_BY_TFIDF, GET_SIMILAR_REPOS_BY_TOPIC, PREDICT_TOPICS
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
        pass
 
if __name__ == '__main__':
    api = GithubCrystalApi()
    
    readme = 'Analyzing trends on Github using topic models and machine learning'
    
    """ How to predict topics. """
    
    topics = api.predict_topics(readme.lower().split())
    print 'Topics'
    for topic_label, percent, topic_id in topics:
        print '\t', topic_label, percent
    
    """ How to get similar repositories by topic. """
    
    # One topics.
    # Note that we have to wrap a single topic since the API expects a list.
    similar_topic_repos = api.get_similar_repos_by_topic([topics[0]])
    print 'Number of repos close to', topics[0][1], 'of', \
        topics[0][0], ':', len(similar_topic_repos)
        
    # Multiple topics.
    similar_topic_repos = api.get_similar_repos_by_topic(topics[:2])
    print 'Number of repos close to', topics[0][1], 'of', \
        topics[0][0], 'and', topics[1][1], 'of', \
        topics[1][0], ':', len(similar_topic_repos)
    print 'IDs:', similar_topic_repos
        
    """ How to get similar repositories by TFIDF. """
    
    # TODO