import os
import pdb
import pickle

def write_important_urls():
  important_indicies = pickle.load(open("important_indicies.p", "rb"))
  important_urls = []
  with open("all_urls.txt", 'rb') as urls:
    for idx, line in enumerate(urls):
      if str(idx) in important_indicies:
        print line
        important_urls.append(line)

  with open("important_urls.txt", 'wb') as out:
    for line in important_urls:
      out.write(line)

def write_pickle():
  with open("important_urls.txt", "rb") as f:
    urls = []
    for idx, line in enumerate(f):
      urls.append(line)
    pickle.dump(urls, open("selected_urls.p", "wb"))

def main():
  # write_important_urls()
  write_pickle()

if __name__ == "__main__":
  main()