import os

if __name__ == '__main__':
    """
    Counts the number of duplicate/empty labels in the specified topic
    label file.
    """
    TOPIC_LABELS_FILE = os.path.join('106k-d_500t_100p_F-2-10', 'clean_topics_106k-d_500t_100p_F-2-10.txt')
    
    EMPTY_LABEL = '___'
    
    labels = set()
    
    num_empty_labels = 0
    num_duplicate_labels = 0
    
    for line in open(TOPIC_LABELS_FILE):
        parts = line.strip().split(',')
        label = parts[1].strip()
        if label in labels:
            print 'Duplicate label', label
            num_duplicate_labels += 1
        elif label != EMPTY_LABEL:
            labels.add(label)
        else:
            num_empty_labels += 1
            
    print 'Number of duplicated labels:', num_duplicate_labels
    print 'Number of empty labels:', num_empty_labels