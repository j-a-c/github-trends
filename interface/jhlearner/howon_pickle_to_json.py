import os
import pdb
import pickle
import json

def convert_pickles():
  metadata = pickle.load(open("clean_metadata.p", "rb"))
  readmes = pickle.load(open("selected_readme.p", "rb"))
  meta_and_readme = pickle.load(open("meta_and_readme.p", "rb"))
  # doc_urls = pickle.load(open('selected_urls.p', 'rb'))
  # indices = pickle.load(open("important_indicies.p", "rb"))

  for key in metadata:
    metadata[key][5] = metadata[key][5].days
  for key in meta_and_readme:
    meta_and_readme[key][5] = meta_and_readme[key][5].days

  json.dump(metadata, open("clean_metadata.json", "wb"))
  json.dump(readmes, open("selected_readme.json", "wb"))
  json.dump(meta_and_readme, open("meta_and_readme.json", "wb"))
  #json.dump(doc_urls, open("selected_urls.json", "wb"))
  #json.dump(indices, open("important_indicies.json", "wb"))

  #GET RID OF DAETTIME FORMAT BEFORE CONVERTING INTO JSON

def main():
  convert_pickles()

if __name__ == "__main__":
  main()