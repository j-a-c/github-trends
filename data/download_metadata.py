import csv
import os
import json
import urllib2


from sorted_directory_iterator import SortedDirectoryIterator
from bs4 import BeautifulSoup

EMPTY = '_'

def test():
    """
    Test to make sure extraction, encoding, and delimiter-quoting works
    correctly.
    """
    
    url = 'https://github.com/torvalds/linux'
    meta = []
    meta.append(get_features(url, -1))
    print meta
    meta.append(["hello, i said", 123, u'\xef'.encode('utf-8'), '"asdf, test"'])
    write_metadata(meta, META_DIR, 'test.txt')
    with open(os.path.join(META_DIR, 'test.txt'), 'r') as meta_file:
        reader = csv.reader(meta_file, delimiter=',', quotechar='"')
        for row in reader:
            for e in row:
                print e.decode('utf-8')

def get_features(url, counter):
    """
    index,
    watch, star, fork, commits, branches, releases, contribs,
    latest_author_date, repo_description, latest_readme_commit, first_readme_commit
    """
    
    features = [counter]

    # Get repo main page.
    response = None
    try:
        response = urllib2.urlopen(url)
    except:
        return features
    repo_html = response.read()
    repo_soup = BeautifulSoup(repo_html)

    # watch, star, fork
    for a in repo_soup.find_all('a', {'class': 'social-count'}):
        try:
            features.append(a.contents[0].strip())
        except:
            features.append(EMPTY)

    # ommits, branches, releases, contribs,
    for s in repo_soup.find_all('span', {'class': 'num text-emphasized'}):
        try:
            features.append(s.contents[0].strip())
        except:
            features.append(EMPTY)

    # latest_author_date
    for t in repo_soup.find_all('time', {'class': 'updated'}):
        features.append(t['datetime'])

    # repo_description
    for d in repo_soup.find_all('div', {'class': 'repository-description'}):
        try:
            features.append(d.contents[0].strip().encode('utf-8'))
        except:
            features.append(EMPTY)
    
    # Find the README name.
    readme_title = None
    for s in repo_soup.find_all('span'):
        try:
            if s.parent.parent.get('id') == 'readme':
                readme_title = s.nextSibling.strip()
        except:
            pass

    # In case we did not get the README name.
    if not readme_title:
        features.append(EMPTY)
        features.append(EMPTY)
        return features
    
    # Get README commit dates.
    readme_commit_url = url + '/commits/master/' + readme_title
    readme_commit_html = None
    try:
        readme_commit_html = urllib2.urlopen(readme_commit_url).read()
    except:
        pass

    if readme_commit_html:
        readme_commit_soup = BeautifulSoup(readme_commit_html)
        timestamps = readme_commit_soup.find_all('time')
        # Find the most recent README commit.
        latest_commit = timestamps[0]['datetime']
        features.append(latest_commit)
        # Find the first README commit.
        first_commit = timestamps[-1]['datetime']
        features.append(first_commit)
    else:
        features.append(EMPTY)
        features.append(EMPTY)

    return features

def write_metadata(metadata_buffer, meta_dir, meta_file_name):
    """
    Write metadata buffer to a file with the same name as the input url file.
    """
    
    with open(os.path.join(meta_dir, meta_file_name), 'w+') as meta_file:
        writer = csv.writer(meta_file, delimiter=',', quotechar='"')
        writer.writerows(metadata_buffer)

if __name__ == '__main__':

    RAW_URL_DIR = os.path.join('..','urls','raw')
    README_INDEX_LIST_FILE = 'clean_readme_index_list.json'
    META_DIR = 'metadata'
    READMES_PER_FILE = 10000

    if not os.path.exists(META_DIR):
        os.mkdir(META_DIR)

    # Construct URL iterator.
    iterator = SortedDirectoryIterator(os.path.join('..', 'urls', 'raw'))

    # Get README index.
    all_readmes = json.load(open(README_INDEX_LIST_FILE))

    # Download metadata for each URL.
    START_INDEX = 0
    counter = 0
    readme_index = 0

    metadata_buffer = []
    for url in iterator:
        # Only process a URL that is in our README list.
        if all_readmes[readme_index] == counter:
            readme_index += 1

            if counter >= START_INDEX:
                # Parse and buffer the data.
                metadata_buffer.append(get_features(url, counter))    
        counter += 1

        # Serialize data.
        if (counter + 1) % READMES_PER_FILE == 0 and len(metadata_buffer) > 0:
            write_metadata(metadata_buffer, META_DIR, str(counter+1-READMES_PER_FILE) + '.txt')
            metadata_buffer = []

    # Write any leftover data.
    if len(metadata_buffer) > 0:
        write_metadata(metadata_buffer, META_DIR, str(counter+1-READMES_PER_FILE) + '.txt')
