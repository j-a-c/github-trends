import os
import shutil
import time
import urllib2

from url_iterator import SortedDirectoryIterator
from bs4 import BeautifulSoup


# Do not change this, it is used to get the raw README.
RAW_PREFIX = 'https://raw.githubusercontent.com'

# The number of READMEs to retrieve this run.
FILES_PER_RUN = 100000

OUTPUT_DIR = 'raw'

def download_readme(url, counter):

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
                        pass
                else:
                    pass

            # Save the README if it has been read
            if raw_readme:
                out_dir = str(int(counter/1000000))
                output_path = os.path.join(os.path.join(OUTPUT_DIR, out_dir, str(counter) + '.md'))

                output = open(output_path, 'w+')
                output.write(raw_readme)
                output.close()

        # Somehow 2+ READMEs were found.
        else:
            pass

    # No README was found
    else:
        pass



if __name__ == '__main__':
    # total_urls = 15493189

    START_INDEX = 14145210
    STOP_INDEX = 14145211
    
    print 'Start index', START_INDEX
    print 'Stop index', STOP_INDEX

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    for i in range(0,16):
        d = os.path.join(OUTPUT_DIR, str(i))
        if not os.path.exists(d):
            os.mkdir(d)

    iterator = SortedDirectoryIterator(os.path.join('..', 'urls', 'raw'))

    counter = 0
    for url in iterator:
        if counter >= START_INDEX and counter < STOP_INDEX:
            try:
                download_readme(url, counter)
            except:
                pass
        counter += 1

    print counter
            
