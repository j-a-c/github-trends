"""
Super hacky script to update the index with some particular urls.
This is used only for the purposes of our final presentation.
"""

import collections
import csv
import gensim
import json
import os
import shutil
import time
import urllib2
import xxhash

from bs4 import BeautifulSoup
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from index import Index

RAW_PREFIX = 'https://raw.githubusercontent.com'

OUTPUT_DIR = os.path.join('..', 'data', 'raw')

CLEAN_ROOT = os.path.join('..', 'data', 'clean')
CLEAN_DIR = CLEAN_ROOT

EMPTY = '_'
META_DIR = os.path.join('..', 'data', 'metadata')

def download_readme(url, counter):

    # Open github page.
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)

    # Determine the current README.
    readme_title = None
    for s in soup.find_all('span'):
        try:
            if s.parent.parent.get('id') == 'readme':
                readme_title = s.nextSibling.strip()
        except:
            pass

    # Find links whose title match the README title.
    readme_links = None
    if readme_title:
        readme_links = [l.get('href') for l in soup.find_all('a') if l.get('title') and l.get('title') == readme_title]
    
    # Possible README found
    if readme_links:

        if len(readme_links) == 1:

            raw_readme_link = readme_links[0]

            # Remove 'blob/' from link. It starts at the third '/'.
            blob_slash_index = raw_readme_link.find('/')
            blob_slash_index = raw_readme_link.find('/', blob_slash_index+1)
            blob_slash_index = raw_readme_link.find('/', blob_slash_index+1)

            raw_readme_link = RAW_PREFIX + raw_readme_link[:blob_slash_index] + raw_readme_link[blob_slash_index+5:]

            # Try to get the README
            raw_readme = None
            try:
                raw_readme = urllib2.urlopen(raw_readme_link).read()
            except:
                if raw_readme_link.endswith('.'):
                    try:
                        raw_readme = urllib2.urlopen(raw_readme_link[:-1]).read()
                    except:
                        pass
                else:
                    pass

            # Save the README if it has been read
            if raw_readme:
                out_dir = str(int(counter/1000000))
                output_path = os.path.join(os.path.join(OUTPUT_DIR, out_dir, str(counter) + '.md'))

                output = open(output_path, 'w+')
                output.write(raw_readme)
                output.close()

        # Somehow 2+ READMEs were found.
        else:
            pass

    # No README was found
    else:
        pass
        
        
# Tokenizes a text. For a sample of the cleaning properties, try code below.
# tokenize(u"\xefgloo10; that's my name, ice-cubes are m3h game!")
def tokenize(text):
    return [token for token in gensim.utils.simple_preprocess(text) if token not in gensim.parsing.preprocessing.STOPWORDS]
   
def get_features(url, counter):
    """
    index,
    watch, star, fork, commits, branches, releases, contribs,
    latest_author_date, repo_description, latest_readme_commit, first_readme_commit
    """
    
    features = [counter]

    # Get repo main page.
    response = None
    try:
        response = urllib2.urlopen(url)
    except:
        return features
    repo_html = response.read()
    repo_soup = BeautifulSoup(repo_html)

    # watch, star, fork
    for a in repo_soup.find_all('a', {'class': 'social-count'}):
        try:
            features.append(a.contents[0].strip())
        except:
            features.append(EMPTY)

    # ommits, branches, releases, contribs,
    for s in repo_soup.find_all('span', {'class': 'num text-emphasized'}):
        try:
            features.append(s.contents[0].strip())
        except:
            features.append(EMPTY)

    # latest_author_date
    for t in repo_soup.find_all('time', {'class': 'updated'}):
        features.append(t['datetime'])

    # repo_description
    for d in repo_soup.find_all('div', {'class': 'repository-description'}):
        try:
            features.append(d.contents[0].strip().encode('utf-8'))
        except:
            features.append(EMPTY)
    
    # Find the README name.
    readme_title = None
    for s in repo_soup.find_all('span'):
        try:
            if s.parent.parent.get('id') == 'readme':
                readme_title = s.nextSibling.strip()
        except:
            pass

    # In case we did not get the README name.
    if not readme_title:
        features.append(EMPTY)
        features.append(EMPTY)
        return features
    
    # Get README commit dates.
    readme_commit_url = url + '/commits/master/' + readme_title
    readme_commit_html = None
    try:
        readme_commit_html = urllib2.urlopen(readme_commit_url).read()
    except:
        pass

    if readme_commit_html:
        readme_commit_soup = BeautifulSoup(readme_commit_html)
        timestamps = readme_commit_soup.find_all('time')
        # Find the most recent README commit.
        latest_commit = timestamps[0]['datetime']
        features.append(latest_commit)
        # Find the first README commit.
        first_commit = timestamps[-1]['datetime']
        features.append(first_commit)
    else:
        features.append(EMPTY)
        features.append(EMPTY)

    return features

def write_metadata(metadata_buffer, meta_dir, meta_file_name):
    """
    Write metadata buffer to a file with the same name as the input url file.
    """
    
    with open(os.path.join(meta_dir, meta_file_name), 'w+') as meta_file:
        writer = csv.writer(meta_file, delimiter=',', quotechar='"')
        writer.writerows(metadata_buffer)   

        
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
                current_index[token] = temp_index[token]
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


def dump_to_disk_topics(temp_index, index_location):
    for topic in temp_index:
        topic_index = temp_index[topic]
        for percent in topic_index:
            f = open(os.path.join(index_location, topic, str(percent) + '.txt'), 'a+')
            for doc in topic_index[percent]:
                f.write(doc + '\n')
            f.close()

        
if __name__ == '__main__':
    
    URLS_TO_INJECT = 'urls_to_inject.txt'

    # For creating the index.
    FILES_PER_DUMP = 500000
    num_readmes_processed = 0
    temp_index = collections.defaultdict(list)
    index = Index(os.path.join('..', 'model', 'index'), None)
    
    # Initialize the counter outside the current url range.
    # This should hopefully let us revert the index to its original state later.
    counter = 51000000
    counter_start = counter

    metadata_buffer = []
    
    new_urls = {}
    new_metadata = {}
    
    for line in open(URLS_TO_INJECT):
        
        url = line.strip()
        
        new_urls[counter] = url
    
        ''' Download README '''
        download_readme(url, counter)
        
        ''' Clean README '''
        dirty_path = os.path.join(OUTPUT_DIR, '51', str(counter) + '.md')
        # clean_path is the same as dirty_path, except DIRTY_ROOT/... is now CLEAN_ROOT/...
        clean_path = os.path.join(CLEAN_ROOT, '51', dirty_path.split(os.path.sep)[-1])
        
        readme = open(dirty_path).readlines()

        # Join all lines in the README with a space.
        readme = ' '.join(readme)
        # Tokenize the README
        readme = tokenize(readme)

        # If README has no valid tokens, do not write anything.
        if len(readme) > 0:
            # Join tokens with a space so we can write to a file.
            readme = ' '.join(readme)

            # Write README
            clean_file = open(clean_path, 'w+')
            # Don't forget to decode('utf-8') when reading later!
            clean_file.write(readme.encode('utf-8'))
            clean_file.close()
        
        ''' Download metadata '''
        new_m = get_features(url, counter)
        new_metadata[counter] = new_m
        metadata_buffer.append(new_m) 
                
        counter += 1
        
    ''' Write metadata '''
    write_metadata(metadata_buffer, META_DIR, str(counter_start) + '.txt')
    
    ''' Update index. '''
    
    d = '51'
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
    
    
    ''' Update topic model index. '''

    """
    Parameters
    """
    MODEL_PATH = os.path.join('..', 'model', '106k-d_500t_100p_F-2-10', 'lda_model.mod')
    IMPORT_DIR = os.path.join('..', 'data', 'clean', '51')

    DICTIONARY_PATH = os.path.join('..', 'model', '106k-d_500t_100p_F-2-10', 'dictionary.dict')

    FILTER = True
    NO_BELOW = 2
    NO_ABOVE = 0.10

    CLASSIFICATION_PATH = 'raw_all_classes.txt'
    CLASSIFY_INPUT_DOCS = True

    ITERATIONS_PER_FILE = 1

    """
    Lazy iterator for accessing files. This allows us to access the files without
    loading them all into memory.
    """
    class MyCorpus(object):
        def __init__(self, directory):
            self.directory = directory

        def __iter__(self):
            for f in os.listdir(self.directory):
                path = os.path.join(self.directory, f)
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
    
    """
    Script to build the topic index.
    """

    #
    # Parameters
    #

    FILES_PER_DUMP = 50000
    RAW_TOPIC_INPUT = 'raw_all_classes.txt'
    PERCENT_WINDOW = 10

    NUM_TOPICS = 500
    
    INDEX_LOCATION = os.path.join('..', 'model', 'topic_index_10')
    
    # Make directories that do not exist.
    
    if not os.path.exists(INDEX_LOCATION):
        os.mkdir(INDEX_LOCATION)
    for t in range(NUM_TOPICS):
        topic_path = os.path.join(INDEX_LOCATION, str(t))
        if not os.path.exists(topic_path):
            os.mkdir(topic_path)
    
    # Build topic index.
    
    temp_index = collections.defaultdict(lambda: collections.defaultdict(list))

    print 'Starting to build index...'
    
    counter = 0
    header = True
    for line in open(RAW_TOPIC_INPUT):
        if header:
            header = False
            continue
    
        parts = line.strip().split()
        
        doc_num = parts[0].split('.')[0]
        
        for part in parts[1:]:
            topic, percent = part.split('/')
            percent = float(percent) * 100
            lower_percent =  int(percent) / PERCENT_WINDOW * PERCENT_WINDOW
            upper_percent =  int(percent + PERCENT_WINDOW) / PERCENT_WINDOW * PERCENT_WINDOW
           
            temp_index[topic][lower_percent].append(doc_num)
            temp_index[topic][upper_percent].append(doc_num)
            
        counter += 1
        if counter % FILES_PER_DUMP == 0:
            dump_to_disk_topics(temp_index, INDEX_LOCATION)
            print 'READMEs processed:', counter
            temp_index = collections.defaultdict(lambda: collections.defaultdict(list))
            
    dump_to_disk_topics(temp_index, INDEX_LOCATION)   

   
    ''' Update id_to_link map '''

    ID_TO_LINK_MAP_PATH = os.path.join('..', 'data', 'id_to_link_map.json')
    
    id_to_link_map = json.load(open(ID_TO_LINK_MAP_PATH))
    
    for k in new_urls:
        id_to_link_map[k] = new_urls[k]
    
    json.dump(id_to_link_map, open(ID_TO_LINK_MAP_PATH, 'w+'))
    
    
    ''' Update links_in_model '''

    LINKS_IN_MODEL_PATH = os.path.join('..', 'data', 'links_in_model.json')
    
    links_in_model = json.load(open(LINKS_IN_MODEL_PATH))
    
    for k in new_urls:
        links_in_model.append(new_urls[k])
    
    json.dump(links_in_model, open(LINKS_IN_MODEL_PATH, 'w+'))
    

    ''' Update metadata index '''
    
    METADATA_INDEX = os.path.join('..', 'data', 'metadata_index.json')
    
    metadata_index = json.load(open(METADATA_INDEX))
    
    meta_file_path =  os.path.join(META_DIR, str(counter_start) + '.txt')
    
    with open(meta_file_path, 'r') as current_meta_file:
        reader = csv.reader(current_meta_file, delimiter=',', quotechar='"')

        for row in reader:
            row = row
            metadata_index[row[0]] = {}
            if len(row) == 1:
                continue
            
            # Catch for a bug in download metadata.
            while len(row) < 12:
                row.insert(-4, '_')
            
            else:
                for e,i in enumerate(row):
                    if i != '_' and e != 0:
                        if e >= 1 and e <= 7:
                            if i.endswith('+'):
                                i = i[:-1]
                            i = int(i.replace(',', ''))
                            if i > 10: # To keep the entries relatively sparse.
                                metadata_index[row[0]][e] = i
                        else:
                            metadata_index[row[0]][e] = i
    
    json.dump(metadata_index, open(METADATA_INDEX, 'w+'))