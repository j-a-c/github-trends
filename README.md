# github-trends
Analyzing trends on Github using topic models and machine learning.

## Usage

First start the server that manages the index:

    python crystal_server.py
    
Then run the user interface:

    python crystal_interface.py
    
An tutorial for the API can be executed by:

    python crystal_api.py

## Dependencies

 - Beautiful Soup: pip install beautifulsoup4
 - gensim: pip install --upgrade gensim
 - xxHash: pip install xxhash