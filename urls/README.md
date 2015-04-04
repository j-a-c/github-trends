# URLs

The Github repository URLs can be found in this directory, within the 7z files. Each archive contains 1 million repository URLs, sorted from oldest to newest. For example, _1m.7z_ contains the first 1 million repository URLs. Within the 7z archives, there are files each containing 50,000 URLs. For example, within the _1m.7z_ archive, the file _0.txt_ contains the first 50,000 links, the file _50,000.txt_ contains the next 50,000 urls, etc. _2m.7_ contains the next 1 million URLs, contained within _1000000.txt_, _1050000.txt_, etc. The URLs are current as of 6pm 4.2.15.

## get_repos.py

This script uses PyGithub to request Github repositories. A CSV file, _credentials.csv_, containing "username, password" must be provided for authentication. _checkpoint.txt_ will be used to record the current progress of the script.

## compress_urls.py

This script compresses the repository URLs downloaded using _get_repos.py_ into the archive format currently in this repository. It can be used to update the archives with new URLs.

## validate.py

Script to validate raw URLs retrieve using _get_repos.py_. This is will print duplicate urls.

