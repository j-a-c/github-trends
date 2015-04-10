import gensim
import os
import re
import shutil
import time

from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS

# Tokenizes a text. For a sample of the cleaning properties, try code below.
# tokenize(u"\xefgloo10; that's my name, ice-cubes are m3h game!")
def tokenize(text):
    return [token for token in gensim.utils.simple_preprocess(text) if token not in gensim.parsing.preprocessing.STOPWORDS]


if __name__ == '__main__':
    DIRTY_ROOT = 'raw'
    CLEAN_ROOT = 'clean'

    # Create directories to hold cleaned, compressed READMEs.
    if not os.path.exists(CLEAN_ROOT):
        os.mkdir(CLEAN_ROOT)
    for i in range(0,16):
        directory = os.path.join(CLEAN_ROOT, str(i))
        if not os.path.exists(directory):
            os.mkdir(directory)

    num_archives_cleaned = 0

    # Clean all READMEs in the dirty folder.
    for root, dirs, files in os.walk(DIRTY_ROOT):
        for f in files:

            dirty_path = os.path.join(root, f)
            # clean_path is the same as dirty_path, except DIRTY_ROOT/... is now CLEAN_ROOT/...
            clean_path = os.path.join(CLEAN_ROOT, os.path.sep.join(dirty_path.split(os.path.sep)[1:]))
            
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

            num_archives_cleaned += 1
            if num_archives_cleaned % 1000 == 0:
                print 'Number of archives cleaned:', num_archives_cleaned

    print 'Number of archives cleaned:', num_archives_cleaned
    print 'Cleaning is done.'
