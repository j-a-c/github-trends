import collections
import gensim
import json
import logging
import os
import time

"""
Script to classify documents using a gensim LDA model.
"""


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

"""
Parameters
"""
MODEL_PATH = os.path.join('106k-d_500t_100p_F-2-10', 'lda_model.mod')
IMPORT_DIR = os.path.join('..', 'data', 'clean')

DICTIONARY_PATH = os.path.join('106k-d_500t_100p_F-2-10', 'dictionary.dict')

FILTER = True
NO_BELOW = 2
NO_ABOVE = 0.10

CLASSIFICATION_PATH = 'raw_all_classes.txt'
CLASSIFY_INPUT_DOCS = True

"""
Lazy iterator for accessing files. This allows us to access the files without
loading them all into memory.
"""
class MyCorpus(object):
    def __init__(self, directory):
        self.directory = directory

    def __iter__(self):
        for d in os.listdir(self.directory):
            root = os.path.join(self.directory, d)
            for f in os.listdir(root):
                path = os.path.join(root, f)
                text = ' '.join(open(path).readlines())
                yield text.lower().split(), path


"""
This is where gensim code starts.
"""

start_time = time.clock()

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
# Classify the documents.
###

print '====='
print 'Classifying documents...'

num_docs_classified = 0
if CLASSIFY_INPUT_DOCS:
    classification_writer = open(CLASSIFICATION_PATH, 'w+')
    classification_writer.write('Document (Topic/Percent)+\n')
    for text,path in MyCorpus(IMPORT_DIR):
        classification_text = path.split(os.path.sep)[-1] + ' '
        for topic, percent in lda_model[dictionary.doc2bow(text)]:
            classification_text += str(topic) + '/' + str(percent) + ' '
        classification_text += '\n'
        classification_writer.write(classification_text)
        
        num_docs_classified += 1
        if num_docs_classified % 10000 == 0:
            print 'Number of documents classified:', num_docs_classified
    classification_writer.close()

print '====='
print 'Total time elapsed:', time.clock() - start_time
