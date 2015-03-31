"""
Convert raw url files into a more manageable compressed format.
"""

import os
import shutil

# Temporary directory name. Will be deleted after use.
TEMP_DIR = 'urls_temp'
# The number of links to include per file.
LINKS_PER_FILE = 50000
# The number of files to include per archive. Currently set up so each archive
# will contain 1 million contiguous urls.
FILES_PER_ZIP = int(1e6 / LINKS_PER_FILE)

url_files = []

# Get all files containing urls.
for root, dirs, files in os.walk('.'):
    for f in files:
            if f.startswith('urls_'):
                url_files.append(f)

# Url file format is url_{url number (1-based)}.
# We will preserve this order.
url_files.sort(key=lambda f: int(f.split('_')[1][:-4]))

urls = []
for url_file in url_files:
    for url in open(url_file):
        urls.append(url)

# Make temporary directory.
if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)


# Merge the url file parts into a temporary directory, with each new file
# containing LINKS_PER_FILE links.
new_url_files = []
for i in range(0, len(urls), LINKS_PER_FILE):
    path = os.path.join(TEMP_DIR, str(i) + '.txt')
    new_url_files.append(path)
    new_file = open(path, 'w+')
    new_file.writelines(urls[i: min(i + LINKS_PER_FILE, len(urls))])
    new_file.close()

# We do not need these data structures any more.
urls = None
new_files = None

# Compress files. Include 1 million contiguous urls per archive.
current_file_number = 1
for i in range(0, len(new_url_files), FILES_PER_ZIP):
    command = '7z a ' + str(current_file_number) + 'm.7z'
    for f in new_url_files[i: min(i + FILES_PER_ZIP, len(new_url_files))]:
        # Include ./ before file name to not include the temporary directory
        # name in the archive.
        command += ' .' + os.path.sep + f
    current_file_number += 1
    os.system(command)

# Delete temporary directory
shutil.rmtree(TEMP_DIR)
