import collections
import json

from clean_text import tokenize

if __name__ == '__main__':
    id_to_link_map = json.load(open('id_to_link_map.json'))
    
    index = collections.defaultdict(list)
    
    for repo_id in id_to_link_map:
        link = id_to_link_map[repo_id].lower()
        
        parts = link.split('/')

        user = parts[2]
        proj_name = parts[3]
        
        index[user].append(repo_id)
        index[proj_name].append(repo_id)
        
        for token in tokenize(proj_name):
            if len(token) > 0:
                index[token].append(repo_id)
                
                
    json.dump(index, open('url_token_index.json', 'w+'))
        
        