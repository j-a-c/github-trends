import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import csv
import pdb
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel

def pickle_readme():
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
        metadata[repo_des] = [_parse(idx), _parse(stars), _parse(forks), _parse(commits), _parse(contributors), delta]
        print row

    pickle.dump(metadata, open("clean_metadata.p", "wb"))
    return metadata

def main():
  # pickle_metadata()
  learn()

if __name__ == "__main__":
  main()