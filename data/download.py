import os
import shutil
import time
import threading
import urllib2

from archive_iterator import ArchiveIterator
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

ERROR_FILE = 'errors.txt'
LOG_FILE = 'log.txt'
RAW_PREFIX = 'https://raw.githubusercontent.com'
TEMP_DIR = 'DOWNLOAD_TEMP_DIR'
FILES_PER_ARCHIVE = 25000

SLEEP_TIME_SECS = 3 * 60

# Used for tracking consecutive URL open errors.
URL_ERROR_SLEEP_TIME_SEC = 5 * 60
MAX_CONSEC_URL_ERRORS = 10
consec_url_errors = 0

ERROR_FILE_LOCK = threading.Lock()


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
    total_urls = 15493189

    START_INDEX = 0
    counter = 0

    errors = open(ERROR_FILE, 'a')
    log = open(LOG_FILE, 'a')

    # Construct the archive iterator
    archive_dir = '..' + os.path.sep
    archive_dir = os.path.join(archive_dir, 'urls')
    archives = [ os.path.join(archive_dir, str(i) + 'm.7z') for i in range(1,17) ]
    iterator = ArchiveIterator(archives)

    files_to_compress = []

    # See if job was stopped early.
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    else:
        files_to_compress = [os.path.join(TEMP_DIR,f) for f in os.listdir(TEMP_DIR)]
        START_INDEX = max([int(f.split('.')[0]) for f in os.listdir(TEMP_DIR)])
        START_INDEX += 1 # Skip the previously written file.
        print 'Adjusting start index to:', START_INDEX

    STOP_INDEX = START_INDEX + FILES_PER_ARCHIVE - ((START_INDEX + FILES_PER_ARCHIVE) % FILES_PER_ARCHIVE)
    urls_to_download = []

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

    while START_INDEX < total_urls:

        for url in iterator:
            if counter < START_INDEX and counter not in incompleted_jobs:
                counter += 1
                continue

            if counter == STOP_INDEX :
                break;
            
            urls_to_download.append( (url.strip(), counter) )
            counter += 1
        
        print 'Starting thread pool.'
        with ThreadPoolExecutor(max_workers=4) as executor:
            for url,counter in urls_to_download:
                executor.submit(download_readme, url, counter, errors, log)
                output_path = os.path.join(TEMP_DIR, str(counter) + '.md')
                files_to_compress.append(output_path)
        

        print 'Compressiong files.'
        # Compress current downloads.
        command = '7z a ' + str(counter) + '.7z'
        for f in files_to_compress:
            # Include ./ before file name to not include the temporary directory
            # name in the archive.
            command += ' .' + os.path.sep + f
        os.system(command)

        shutil.rmtree(TEMP_DIR)
        os.mkdir(TEMP_DIR)
        os.system('rm ' + LOG_FILE)

        counter = 0
        files_to_compress = []
        incompleted_jobs.clear()
        START_INDEX = STOP_INDEX
        STOP_INDEX = START_INDEX + FILES_PER_ARCHIVE

        time.sleep(SLEEP_TIME_SECS)

