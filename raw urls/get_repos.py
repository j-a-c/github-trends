import time

from github import Github

SLEEP_TIME_SECS = 1
QUIT_COUNTER = 50000

# Since
since = 2916227

# Counter
counter = 1185184

# A CSV file with username,password for your Github
credentials = ''.join(open('credentials.csv').readlines()).split(',')

g = Github(credentials[0].strip(), credentials[1].strip())


url_buffer = []
last_id = None

while True:
    new_counter = 0
    url_file = open('urls_' + str(counter+1) + '.txt', 'w+')
    for repo in g.get_repos(since = since):
        url_buffer.append( repo.html_url + '\n' )

        if len(url_buffer) > 1000:
            url_file.writelines(url_buffer)
            counter += len(url_buffer)
            new_counter += len(url_buffer)
            url_buffer = []
            last_id = repo.id
            print 'URLs written:', counter, 'Last id:', last_id
            if new_counter >= QUIT_COUNTER:
                since = last_id
                break
            time.sleep(SLEEP_TIME_SECS)
