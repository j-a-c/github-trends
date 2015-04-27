import os

url_files = os.listdir('.')
url_files = [int(fn.replace('.txt', '')) for fn in url_files if fn.endswith('.txt')]
url_files.sort()
url_files = [str(fn)+'.txt' for fn in url_files]

for fn in url_files:
	if fn.endswith('.txt'):
		with open(fn, 'rb') as f:
			print fn
			content = [line for line in f]
		
		with open("all_urls.txt", 'a') as out:
			for line in content:
				out.write(line)