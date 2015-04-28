import collections
import os

def dump_to_disk(temp_index, index_location):
    for topic in temp_index:
        topic_index = temp_index[topic]
        for percent in topic_index:
            f = open(os.path.join(index_location, topic, str(percent) + '.txt'), 'a+')
            for doc in topic_index[percent]:
                f.write(doc + '\n')
            f.close()
        

if __name__ == '__main__':
    """
    Script to build the topic index.
    """

    #
    # Parameters
    #

    FILES_PER_DUMP = 50000
    RAW_TOPIC_INPUT = 'raw_all_classes_1_iter.txt'
    PERCENT_WINDOW = 10

    NUM_TOPICS = 500
    
    INDEX_LOCATION = 'topic_index'
    
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
            dump_to_disk(temp_index, INDEX_LOCATION)
            print 'READMEs processed:', counter
            temp_index = collections.defaultdict(lambda: collections.defaultdict(list))
            
    dump_to_disk(temp_index, INDEX_LOCATION)
