import os
import shutil

url_files = []

# Get all files containing urls.
for root, dirs, files in os.walk('.'):
    for f in files:
            if f.startswith('urls_'):
                url_files.append(f)

# Url file format is url_{url number (1-based)}.
# We will preserve this order.
url_files.sort(key=lambda f: int(f.split('_')[1][:-4]))

urls = {}
for url_file in url_files:
    for url in open(url_file):
        if url not in urls:
            urls[url] = url_file
        else:
            print 'Duplicate url:', url.strip(), 'Originally in:', urls[url], 'Found in:', url_file
