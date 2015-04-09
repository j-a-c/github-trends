import os
import shutil
import time
import threading
import urllib2

from archive_iterator import ArchiveIterator
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Number of workers for parallel README downloads.
NUM_WORKERS = 4

# Do not change this, it is used to get the raw README.
RAW_PREFIX = 'https://raw.githubusercontent.com'

# The number of READMEs to retrieve this run.
FILES_PER_RUN = 100000

# Sleep time between jobs.
SLEEP_TIME_SECS = 30

# Used internally to track state.
ERROR_FILE = 'errors.txt'
LOG_FILE = 'log.txt'
ERROR_FILE_LOCK = threading.Lock()
# Downloads will be stored here.
TEMP_DIR = 'DOWNLOAD_TEMP_DIR'


def download_readme(url, counter, errors, log):

    ERROR_FILE_LOCK.acquire()
    log.write('Starting ' + str(counter) + '\n')
    ERROR_FILE_LOCK.release()

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
                        ERROR_FILE_LOCK.acquire()
                        error = url + ' Error reading URL: ' + raw_readme_link +'. Position: ' + str(counter) + '\n'
                        errors.write(error)
                        ERROR_FILE_LOCK.release()
                else:
                    ERROR_FILE_LOCK.acquire()
                    error = url + ' Error reading URL: ' + raw_readme_link +'. Position: ' + str(counter) + '\n'
                    errors.write(error)
                    ERROR_FILE_LOCK.release()

            # Save the README if it has been read
            if raw_readme:
                output_path = os.path.join(TEMP_DIR, str(counter) + '.md')

                output = open(output_path, 'w+')
                output.write(raw_readme)
                output.close()

        # Somehow 2+ READMEs were found.
        else:
            ERROR_FILE_LOCK.acquire()
            error = url + ' Too many READMEs found. Position: ' + str(counter) + '\n'
            errors.write(error)
            ERROR_FILE_LOCK.release()

    # No README was found
    else:
        ERROR_FILE_LOCK.acquire()
        error = url + ' No README found. Position: ' + str(counter) + '\n'
        errors.write(error)
        ERROR_FILE_LOCK.release()

    ERROR_FILE_LOCK.acquire()
    log.write('Ending ' + str(counter) + '\n')
    ERROR_FILE_LOCK.release()


if __name__ == '__main__':
    # total_urls = 15493189

    START_INDEX = 0
    counter = 0

    errors = open(ERROR_FILE, 'a')
    log = open(LOG_FILE, 'a')

    # Construct the archive iterator
    archive_dir = os.path.join('..', 'urls', archive)
    archives = [ os.path.join(archive_dir, str(i) + 'm.7z') for i in range(1,17) ]
    iterator = ArchiveIterator(archives)

    files_to_compress = []

    # If no temporary directory exists..
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
        # See if any archives have been completed.
        completed_indices = [int(a.split('.')[0]) for a in os.listdir('.') if a.endswith('.7z')]
        if len(completed_indices) > 0:
            START_INDEX = max(completed_indices)
    else: # See where we stopped last.
        files_to_compress = [os.path.join(TEMP_DIR,f) for f in os.listdir(TEMP_DIR)]
        START_INDEX = max([int(f.split('.')[0]) for f in os.listdir(TEMP_DIR)])
        START_INDEX += 1 # Skip the previously written file.
        print 'Adjusting start index to:', START_INDEX

    STOP_INDEX = START_INDEX + FILES_PER_RUN - ((START_INDEX + FILES_PER_RUN) % FILES_PER_RUN)
    urls_to_download = []

    print 'Start index', START_INDEX
    print 'Stop index', STOP_INDEX

    # Load any incompleted jobs.
    incompleted_jobs = set()
    for line in open(LOG_FILE):
        if len(line.strip().split()) < 2:
            continue
        job = int(line.strip().split()[-1])
        if job not in incompleted_jobs:
            incompleted_jobs.add(job)
        else:
            incompleted_jobs.remove(job)


    for url in iterator:
        if counter < START_INDEX and counter not in incompleted_jobs:
            counter += 1
            continue

        if counter == STOP_INDEX :
            break;
        
        urls_to_download.append( (url.strip(), counter) )
        counter += 1
    
    print 'Starting thread pool.'
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        for url,counter in urls_to_download:
            executor.submit(download_readme, url, counter, errors, log)
            output_path = os.path.join(TEMP_DIR, str(counter) + '.md')
            files_to_compress.append(output_path)
