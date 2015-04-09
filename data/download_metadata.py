import csv
import os
import urllib2


from archive_iterator import ArchiveIterator
from bs4 import BeautifulSoup

NUM_META_PER_FILE = 5000

def write_metadata(metadata_buffer, counter):
    # Normalize counter.
    todo

    # Write metadata to csv file.
    todo

if __name__ == '__main__':

    # Construct URL archive iterator.
    archive_dir = '..' + os.path.sep
    archive_dir = os.path.join(archive_dir, 'urls')
    archives = [ os.path.join(archive_dir, str(i) + 'm.7z') for i in range(1,17) ]
    archive_iterator = ArchiveIterator(archives)

    # Get and sort all the cleaned READMEs.
    # We will use these files because some raw READMEs may have not have
    # survived cleaning.
    all_readmes = []
    todo

    # Download metadata for each URL.
    counter = 0
    readme_index = 0
    metadata_buffer = []
    for url in archive_iterator:
        # Only process a URL that is in our README list.
        if all_readmes[readme_index] == counter:
            response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html)

            # Find the data.
            todo
            for s in soup.find_all('span'):
                try:
                    if s.parent.parent.get('id') == 'readme':
                        readme_title = s.nextSibling.strip()
                except:
                    pass

            # Buffer the data.
        
        counter += 1

        # Serialize data.
        if counter % NUM_META_PER_FILE == 0:
            write_metadata(metadata_buffer, counter)
            metadata_buffer = []
            
    # Serialize any remaining metadata.
    write_metdata(metadata_buffer, counter)
