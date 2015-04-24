import collections
import gensim
import json
import logging
import os
import time

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

"""
Parameters
"""

IMPORT_DIR = os.path.join('..', 'data', 'lda_sample')

# Temporary data structure parameters.
CORPORA_PATH = 'corpus.mm'
DICTIONARY_PATH = 'dictionary.dict'

# Model parameters
NUM_TOPICS = 1000 # The number of topics to find.
NUM_PASSES = 25 # The number of passes to make over the corpus.

# Filter parameters
FILTER = True
NO_BELOW = 50
NO_ABOVE = 0.20

# Output parameters
N_TOP_WORDS = 25 # The number of top words to show per topic.
TOPIC_FILE = 'topics.txt'
CLASSIFICATION_PATH = 'classes.txt'
CLASSIFY_INPUT_DOCS = False

"""
Lazy iterator for accessing files. This allows us to access the files without
loading them all into memory.
"""
class MyCorpus(object):
    def __init__(self, directory):
        self.directory = directory

    def __iter__(self):
        for root, dirs, files in os.walk(self.directory):
            for f in files:
                path = os.path.join(root, f)
                text = ' '.join(open(path).readlines())
                yield text.lower().split(), path


"""
This is where gensim code starts.
"""

start_time = time.clock()

###
# Create the dictionary.
###

print 'Creating dictionary...'

dict_start_time = time.clock()
dictionary = None
if not os.path.isfile(DICTIONARY_PATH):
    dictionary = gensim.corpora.Dictionary(text for text,_ in MyCorpus(IMPORT_DIR))
    dictionary.save(DICTIONARY_PATH)
dictionary = gensim.corpora.Dictionary.load(DICTIONARY_PATH)

print '\t', dictionary
print '\tTime to create dictionary:', time.clock() - dict_start_time

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
# Serialize the corpus.
###

print '====='
print 'Serializing corpus...'

serialize_start_time = time.clock()
if not os.path.isfile(CORPORA_PATH):
    corpus = [dictionary.doc2bow(text) for text,_ in MyCorpus(IMPORT_DIR)]
    gensim.corpora.MmCorpus.serialize(CORPORA_PATH, corpus)
    corpus = None
mm = gensim.corpora.MmCorpus(CORPORA_PATH)

print '\t', mm
print '\tTime to serialize:', time.clock() - serialize_start_time

###
# Train the model.
###

print '====='
print 'Training model...'

train_start_time = time.clock() 
lda_model = gensim.models.ldamodel.LdaModel(corpus=mm, num_topics=NUM_TOPICS, \
    id2word=dictionary, update_every=0, passes=NUM_PASSES, alpha='auto')

print '\tTime to train', time.clock() - train_start_time

###
# Save the model.
###
    
print '====='
print 'Saving model...'
    
lda_model.save('lda_model.mod')
    
###
# Write the topics.
###

print '====='
print 'Writing topics...'

topic_writer = open(TOPIC_FILE, 'w+')
topic_writer.write(json.dumps(list(lda_model.alpha)) + '\n')
for topic_id in range(NUM_TOPICS):
    topic_string = str(topic_id) + ' '
    for p,w in lda_model.show_topic(topic_id, topn=N_TOP_WORDS):
        topic_string += str(p) + '*' + w + ' '
    topic_string += '\n'
    topic_writer.write(topic_string.encode('utf-8'))
topic_writer.close()

###
# Classify the documents.
###

print '====='
print 'Classifying documents...'

if CLASSIFY_INPUT_DOCS:
    classification_writer = open(CLASSIFICATION_PATH, 'w+')
    for text,path in MyCorpus(IMPORT_DIR):
        classification_text = path + ' '
        for topic, percent in lda_model[dictionary.doc2bow(text)]:
            classification_text += str(topic) + ' ' + str(percent) + ' '
        classification_text += '\n'
        classification_writer.write(classification_text)
    classification_writer.close()

print '====='
print 'Total time elapsed:', time.clock() - start_time
