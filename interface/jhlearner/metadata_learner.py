import csv
import numpy as np
import os
import pdb
import pickle
import requests
import sys

from base64 import b64decode as decoder
from datetime import datetime
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    import BeautifulSoup
except:
    from bs4 import BeautifulSoup

# Tokenizes a text. For a sample of the cleaning properties, try code below.
# tokenize(u"\xefgloo10; that's my name, ice-cubes are m3h game!")

ADDITIONAL_STOPWORDS = set(['xxhash'])
CUSTOM_STOPWORDS = ADDITIONAL_STOPWORDS.union(STOPWORDS)

def tokenize(text):
  return [token for token in simple_preprocess(text) if token not in CUSTOM_STOPWORDS]

def dedup(arr):
  new_arr = []
  for el in arr:
    if el not in new_arr:
      new_arr.append(el)
  return new_arr

def get_description(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text)
  description = soup.find_all('div', {'class': 'repository-description'})
  return description

def _parse(num):
  if num == '_':
    return 0
  try:
    return int(num)
  except:
    return int(num.replace(",", "").replace("+", ""))

def pickle_metadata():
  metadata = {}

  with open("weeded_out_data.txt", 'rb') as f:
    reader = csv.reader(f)

    for row in reader:
      if len(row) == 12:
        idx, watches, stars, forks, commits, branches, release, contributors, author_date, repo_des, last_readme, first_readme = row

      elif len(row) == 11: #missing author_date
        idx, watches, stars, forks, commits, branches, release, contributors, repo_des, last_readme, first_readme = row

      else:
        continue

      if (last_readme != '_' and first_readme != '_'):
        last_readme_formatted = datetime.strptime(last_readme[:10], "%Y-%m-%d")
        first_readme_formatted = datetime.strptime(first_readme[:10], "%Y-%m-%d")
        delta = last_readme_formatted - first_readme_formatted

      if repo_des:
        # metadata[repo_des] = [_parse(idx), _parse(stars), _parse(forks), _parse(commits), _parse(contributors), delta]
        metadata[_parse(idx)] = [repo_des, _parse(stars), _parse(forks), _parse(commits), _parse(contributors), delta]
        print row

    pickle.dump(metadata, open("clean_metadata.p", "wb"))
    return metadata

def combine_description_and_readme():
  metadata = pickle.load(open("clean_metadata.p", "rb"))
  readmes = pickle.load(open("selected_readme.p", "rb"))
  meta_and_readme = {}

  num_success = 0
  num_fail = 0
  failed_keys = set()
  for key in metadata:
    try:
      readme = readmes[str(key)]
      num_success += 1

      combined = metadata[key][0] + readme
      meta_and_readme[combined] = [key] + metadata[key][1:]

    except:
      num_fail += 1
      failed_keys.add(key)


  # pdb.set_trace()

  pickle.dump(meta_and_readme, open("meta_and_readme.p", "wb"))
  return meta_and_readme

# just compare the first document with everything else
def learn_test():
  data = pickle.load(open("meta_and_readme.p", "rb"))
  documents = data.keys()
  tfidf = TfidfVectorizer()
  trained_model = tfidf.fit_transform(documents)

  cosine_similarities = linear_kernel(trained_model[0:1], trained_model).flatten()

  related_docs_indices = cosine_similarities.argsort()[:-6:-1] # return top 5 indices

def get_readme_content(repo_url, username, pw):
  pathname = repo_url[repo_url.find("github.com/")+11:]
  owner, repo = pathname.split('/')
  readme_url = "https://api.github.com/repos/" + pathname + "/readme"
  # response2 = requests.get(readme_url, auth=('some_username', 'some_pw'))
  response2 = requests.get(readme_url, auth=(username, pw))
  
  json_data = response2.json()

  encoded_content = json_data['content']
  readme_content = decoder(encoded_content)
  return readme_content

def get_repo(repo_url, username, pw):
  pathname = repo_url[repo_url.find("github.com/")+11:]
  owner, repo = pathname.split('/')

  stats_url = "https://api.github.com/repos/" + pathname

  response1 = requests.get(stats_url, auth=(username, pw))
  json_data1 = response1.json()

  #readme_content = get_readme_content(repo_url, username, pw)

  # tokens = ' '.join(dedup(tokenize(readme_content)))

  #pdb.set_trace()

  try:
    obj = {
      'full_name': json_data1['full_name'],
      "description": json_data1['description'],
      'stars_count': json_data1['stargazers_count'],
      'watchers_count': json_data1['watchers_count'],
      'forks_count': json_data1['forks_count'],
      'issues_count': json_data1['open_issues_count'],
      'repo_size': json_data1['size'],
      #'readme_content': readme_content,
      #'tokens': tokens,
    }
  except:
    obj = {}

  return obj

def learn(repo_url, username, pw):
  data = pickle.load(open(os.path.join('interface', 'jhlearner', 'meta_and_readme.p'), 'rb'))
  doc_urls = pickle.load(open(os.path.join('interface', 'jhlearner', 'selected_urls.p'), 'rb'))

  documents = data.keys()
  tfidf = TfidfVectorizer()
  trained_model = tfidf.fit_transform(documents)

  readme_content = get_readme_content(repo_url, username, pw)

  # TODO: append description text to the readme content for more accurate results

  document = ' '.join(dedup(tokenize(readme_content)))

  test_model = tfidf.transform([document])
  cosine_similarities = linear_kernel(test_model, trained_model).flatten()
  related_docs_indices = cosine_similarities.argsort()[:-6:-1]

  results = []
  
  for idx in related_docs_indices:
    similarity = cosine_similarities[idx]
    doc_as_key = documents[idx]
    repo_metadata = data[doc_as_key]
    real_idx = str(repo_metadata[0])
    doc_url = doc_urls[real_idx]
    repo_metadata.append(similarity)
    repo_metadata.append(doc_url)
    results.append(repo_metadata)

  print "\nINPUT:", repo_url
  print "\nSIMILAR REPOS"
  print "=============================="

  result_objs = []

  for result in results:
    idx, stars, forks, commits, contributors, delta, similarity, repo_url = result
    result_obj = {
      'idx': idx,
      'stars': stars,
      'forks': forks,
      'commits': commits,
      'num_contributors': contributors,
      'days_active': delta.days,
      # 'similarity': similarity,
      'similarity': "{0:.2f}".format(similarity),
      'repo_url': repo_url
    }
    result_objs.append(result_obj)

    
    # print "idx:", idx, "stars:", stars, "forks:", forks, "commits:", commits, "contributors:", contributors, "days:", delta.days, "similarity:", similarity
    # print "url:", doc_url, "\n"

  return result_objs


def important_indicies(data, pickle=False):
  if not data:
    data = pickle.load(open("clean_metadata.p", "rb"))
  indicies = set([str(data[k][0]) for k in data.keys()])
  
  if pickle:
    pickle.dump(indicies, open("important_indicies.p", "wb"))
  return indicies

def main():
  if len(sys.argv) > 1:
    repo_url = sys.argv[1]
  else:
    repo_url = "https://github.com/scikit-learn/scikit-learn"

  learn(repo_url)

if __name__ == "__main__":
  main()