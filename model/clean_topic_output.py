import os
import sys

if __name__ == '__main__':
    """
    Script to clean output produced by gensim document classification.
    The actual format is from classify_documents.py.
    """
    
    if len(sys.argv) != 2:
        print 'Usage: python clean_topic_output.py TOPIC_FILE'
        quit()

    input_file = sys.argv[1]
    output_file = input_file.split(os.path.sep)
    output_file[-1] = 'clean_' + output_file[-1]
    output_file = os.path.join(*output_file)
    writer = open(output_file, 'w+')

    header = True
    for line in open(input_file):
        if header:
            header = False
            continue
        
        parts = line.strip().split()
        
        clean_line = parts[0] +', ___ ,'
        for part in parts[1:]:
            clean_line += ' ' + part.split('*')[-1]
        clean_line += '\n'
        
        writer.write(clean_line)
    writer.close()
        
