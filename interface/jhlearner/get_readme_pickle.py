import os
import pdb
import pickle

def write_readme_content():
  important_indicies = pickle.load(open("important_indicies.p", "rb"))
  for root, subdirs, files in os.walk('.'):
    for fn in files:
      all_readme_content = [] # in one subdir
      fn_num = fn.replace(".md", "")
      if fn_num in important_indicies:
        fullpath = os.path.join(root, fn)
        with open(fullpath, 'rb') as f:
          readme_content = []
          for line in f:
            readme_content.append(line.strip())
          readme_content.append('\n')
          content = [fn_num] + readme_content
          content_str = ' '.join(content)
          all_readme_content.append(content_str)

      with open('all_readme.txt', 'a') as all_readme:
        for line in all_readme_content:
          print line
          all_readme.write(line)

def write_pickle():
  with open("all_readme.txt", "rb") as f:
    all_readme = {}
    for line in f:
      idx = line[0:line.index(' ')]
      readme = line[line.index(' '):]
      all_readme[idx] = readme
    pickle.dump(all_readme, open("selected_readme.p", "wb"))

def main():
  write_pickle()

if __name__ == "__main__":
  main()