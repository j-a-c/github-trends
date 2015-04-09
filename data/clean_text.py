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
    TEMP_DIRTY_DIR = 'CLEANING_TEMP_DIRTY_DIR'
    TEMP_CLEAN_DIR = 'CLEANING_TEMP_CLEAN_DIR'

    # Create directories to hold cleaned, compressed READMEs.
    if not os.path.exists(CLEAN_ROOT):
        os.mkdir(CLEAN_ROOT)
    for i in range(1,17):
        directory = os.path.join(CLEAN_ROOT, str(i) + 'm')
        if not os.path.exists(directory):
            os.mkdir(directory)

    # Remove temporary directories if they exists already.
    if os.path.exists(TEMP_DIRTY_DIR):
        shutil.rmtree(TEMP_DIRTY_DIR)
    if os.path.exists(TEMP_CLEAN_DIR):
        shutil.rmtree(TEMP_CLEAN_DIR)

    num_archives_cleaned = 0

    # Clean all READMEs in the dirty folder.
    for root, dirs, archives in os.walk(DIRTY_ROOT):
        for archive in archives:
            # Create directory to hold extracted files.
            os.mkdir(TEMP_DIRTY_DIR)
            os.mkdir(TEMP_CLEAN_DIR)
            
            # Extract READMES.
            command = '7z e -o' + TEMP_DIRTY_DIR + ' ' + os.path.join(root, archive)
            os.system(command)

            prev_dir = root.split(os.path.sep)[-1]

            # Clean READMES.
            for f in os.listdir(TEMP_DIRTY_DIR):
                readme = open(os.path.join(TEMP_DIRTY_DIR, f)).readlines()
                # Join all lines in the README with a space.
                readme = ' '.join(readme)
                # Tokenize the README
                readme = tokenize(readme)
                # If README has no valid tokens, do not write anything.
                if len(readme) == 0:
                    continue
                # Join tokens with a space so we can write to a file.
                readme = ' '.join(readme)

                # Write README
                clean_file = open(os.path.join(CLEAN_ROOT, prev_dir, f), 'w+')
                # Don't forget to decode('utf-8') when reading later!
                clean_file.write(readme.encode('utf-8'))
                clean_file.close()

            # In case we ever need to compress the README instead of writing directly.
            """
            # If no README is the current archive had valid tokens, do not create a clean archive.
            if len(os.listdir(TEMP_CLEAN_DIR)) == 0:
                # Remove temporary directories.
                shutil.rmtree(TEMP_DIRTY_DIR)
                shutil.rmtree(TEMP_CLEAN_DIR)
                continue

            # Compress and move READMEs.
            prev_dir = root.split(os.path.sep)[-1]
            command = '7z a ' + os.path.join(os.path.join(CLEAN_ROOT, prev_dir), archive)
            # Include ./ before file name to not include the temporary directory
            # name in the archive.
            command += ' .' + os.path.sep
            command += TEMP_CLEAN_DIR + os.path.sep + '*'
            os.system(command)
            """

            # Remove temporary directories.
            shutil.rmtree(TEMP_DIRTY_DIR)
            shutil.rmtree(TEMP_CLEAN_DIR)

            num_archives_cleaned += 1

    print 'Number of archives cleaned:', num_archives_cleaned
