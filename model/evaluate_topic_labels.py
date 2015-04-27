import collections
import os

if __name__ == '__main__':
    """
    Counts the number of duplicate/empty labels in the specified topic
    label file.
    """
    TOPIC_LABELS_FILE = os.path.join('106k-d_500t_100p_F-2-10', 'clean_topics_106k-d_500t_100p_F-2-10.txt')
    
    EMPTY_LABEL = '___'
    
    labels = collections.defaultdict(int)
    
    num_empty_labels = 0
    num_duplicate_labels = 0
    num_total_topics = 0
    
    for line in open(TOPIC_LABELS_FILE):
        parts = line.strip().split(',')
        label = parts[1].strip().lower()
        
        num_total_topics += 1
        if label != EMPTY_LABEL:
            labels[label] += 1
        else:
            num_empty_labels += 1
     
    print 'Duplicated labels:'
    for label in labels:
        if labels[label] > 1:
            print '\t', label, labels[label]
        
    print 'Number of empty labels:', num_empty_labels
    print 'Total topics', num_total_topics