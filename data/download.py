import os
import shutil
import time
import urllib2

from archive_iterator import ArchiveIterator
from bs4 import BeautifulSoup

ERROR_FILE = 'errors.txt'
RAW_PREFIX = 'https://raw.githubusercontent.com'
TEMP_DIR = 'DOWNLOAD_TEMP_DIR'
FILES_PER_ARCHIVE = 10000

SLEEP_TIME_SECS = 1 * 60

START_INDEX = 0


# Used for tracking consecutive URL open errors.
URL_ERROR_SLEEP_TIME_SEC = 5 * 60
MAX_CONSEC_URL_ERRORS = 10
consec_url_errors = 0


counter = 0

if __name__ == '__main__':
    errors = open(ERROR_FILE, 'a')

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

    for url in iterator:
        if counter < START_INDEX:
            counter += 1
            continue

        # Open github page.
        url = url.strip()
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

                raw_readme = None
                try:
                    raw_readme = urllib2.urlopen(raw_readme_link).read()
                except:
                    error = url + ' Error reading URL: ' + raw_readme_link +'. Position: ' + str(counter) + '\n'
                    errors.write(error)

                    consec_url_errors += 1
                    if consec_url_errors >= MAX_CONSEC_URL_ERRORS:
                        consec_url_errors = 0
                        time.sleep(URL_ERROR_SLEEP_TIME_SEC)

                output_path = os.path.join(TEMP_DIR, str(counter) + '.md')
                files_to_compress.append(output_path)

                output = open(output_path, 'w+')
                output.write(raw_readme)
                output.close()

                consec_url_errors = 0

            # Somehow 2+ READMEs were found.
            else:
                error = url + ' Too many READMEs found. Position: ' + str(counter) + '\n'
                errors.write(error)
 
        # No README was found
        else:
            error = url + ' No README found. Position: ' + str(counter) + '\n'
            errors.write(error)
        
        counter += 1
        
        if counter % FILES_PER_ARCHIVE == 0:

            command = '7z a ' + str(counter) + '.7z'
            for f in files_to_compress:
                # Include ./ before file name to not include the temporary directory
                # name in the archive.
                command += ' .' + os.path.sep + f
            os.system(command)

            shutil.rmtree(TEMP_DIR)
            os.mkdir(TEMP_DIR)
            files_to_compress = []

            time.sleep(SLEEP_TIME_SECS)

