import json
import os

if __name__ == '__main__':
    
    PROPOSED_URLS = 'proposed_urls.txt'
    
    LINKS_IN_MODEL = os.path.join('..', 'data', 'links_in_model.json')
    
    OUTPUT = 'urls_to_inject.txt'
    
    # Load links in the model.
    links_in_model = json.load(open(LINKS_IN_MODEL))
    
    output = open(OUTPUT, 'w+')
    
    for line in open(PROPOSED_URLS):
        url = line.strip()
        if not url.startswith('#') and len(url) > 0 and url not in links_in_model:
            output.write(url + '\n')
            
    output.close()