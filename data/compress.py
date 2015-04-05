import os

TEMP_DIR = 'DOWNLOAD_TEMP_DIR'

inc = 5000
start = 25000
end = start + inc

files_to_compress = []
for f in os.listdir(TEMP_DIR):
    n = int(f.split('.')[0])
    if n >= start and n < end:
        files_to_compress.append(os.path.join(TEMP_DIR,f))


command = '7z a ' + str(end) + '.7z'
for f in files_to_compress:
    # Include ./ before file name to not include the temporary directory
    # name in the archive.
    command += ' .' + os.path.sep + f
os.system(command)
print 'done'
