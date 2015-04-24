import os
import random
import shutil

if __name__ == '__main__':

    INPUT_DIR = 'clean'
    OUTPUT_DIR = 'lda_sample'
    
    PERCENT_TO_KEEP = 0.20

    for root, dirs, files in os.walk(INPUT_DIR):
        for f in files:
            if random.random() > PERCENT_TO_KEEP: 
                continue
            old_path = os.path.join(root, f)
            new_path = os.path.join(OUTPUT_DIR, f)
            shutil.copyfile(old_path, new_path)