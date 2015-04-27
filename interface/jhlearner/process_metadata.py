import os
import csv
import pdb

def combine_data():

  lines = []

  for file_name in os.listdir('.'):
    if file_name.endswith('.txt'):
      print (file_name, "is read")
      with open(file_name, 'rb') as f:
        for line in f:
          lines.append(line)

  with open("combined_data.txt", 'wb') as f2:
    for line in lines:
      f2.write(line)
      print line

def _parse(num):
  if num == '_':
    return 0
  try:
    return int(num)
  except:
    return int(num.replace(",", "").replace("+", ""))

def weed_out_data():
  selected_lines = []

  # Select data that meet minimum num stars + watchers + forks
  with open("combined_data.txt", 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
      if len(row) == 12:
        idx, watches, stars, forks, commits, branches, release, contributors, author_date, repo_des, last_readme, first_readme = row
      elif len(row) == 11: #missing author_date
        idx, watches, stars, forks, commits, branches, release, contributors, repo_des, last_readme, first_readme = row
        
      if (_parse(stars) > 5 and _parse(forks) > 5 and _parse(commits) > 10 and _parse(contributors) > 1):
        print row
        selected_lines.append(row)

  with open("weeded_out_data.txt", 'wb') as f2:
    writer = csv.writer(f2)
    for line in selected_lines:
      writer.writerow(line)

def main():
  print "weeding out!!"
  weed_out_data()

if __name__ == "__main__":
  main()

