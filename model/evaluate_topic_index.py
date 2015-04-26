import os        

if __name__ == '__main__':
    """
    Produces some rough statistics on the topic index distribution.
    """

    NUM_TOPICS = 500
    
    PERCENT_WINDOW = 2
    
    INDEX_LOCATION = 'topic_index'
    
    expected_number_file_per_topic = (100 / PERCENT_WINDOW) + 1
    
    max_topic_percent = []
    max_docs_per_file = 0
    min_docs_per_file = float('inf')
    
    for t in range(NUM_TOPICS):
        topic_path = os.path.join(INDEX_LOCATION, str(t))
        
        file_counter = 0
        for p in os.listdir(topic_path):
            percent_path = os.path.join(topic_path, p)
            line_counter = 0
            for line in open(percent_path):
                line_counter += 1
                
            if line_counter > max_docs_per_file:
                max_docs_per_file = line_counter
                max_topic_percent = [t, p]
            elif line_counter < min_docs_per_file:
                min_docs_per_file = line_counter
            
            file_counter += 1
        
        if expected_number_file_per_topic != file_counter:
            print 'Expected', expected_number_file_per_topic, 'found', file_counter, 'in topic', t
            
    print 'max_docs_per_file', max_docs_per_file
    print '\t', max_topic_percent
    print 'min_docs_per_file', min_docs_per_file