import time

from github import Github

STATUS_FILE = 'checkpoint.txt'
EXCEPT_TIME_SECS = 5 * 60
SLEEP_TIME_SECS = 1
QUIT_COUNTER = 50000

# 'Since' parameter for Github repository pagination API
since = 27549839

# Counter for total number of URLs received.
counter = 15493478

# A CSV file with username,password for your Github
credentials = ''.join(open('credentials.csv').readlines()).split(',')

g = Github(credentials[0].strip(), credentials[1].strip())


while True:
    try:
        url_buffer = []
        last_id = None

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

                status = 'URLs written: ' + str(counter) + ' Last id: ' + str(last_id)
                print status
                
                f = open(STATUS_FILE, 'w+')
                f.write(status)
                f.close()
                
                since = last_id

                if new_counter >= QUIT_COUNTER:
                    break
                time.sleep(SLEEP_TIME_SECS)
    except:
        print 'Exception caught. Now sleeping'
        time.sleep(EXCEPT_TIME_SECS)
