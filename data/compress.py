import os
import time

RAW = 'raw'
TEMP_DIR = 'DOWNLOAD_TEMP_DIR'

inc = 5000
start = 0
end = start + inc


def get_n(path):
    return int(path.split(os.path.sep)[-1].split('.')[0])

if __name__ == '__main__':
    # Create directories to hold compressed READMEs.
    if not os.path.exists(RAW):
        os.mkdir(RAW)
    for i in range(1,17):
        directory = os.path.join(RAW, str(i) + 'm')
        if not os.path.exists(directory):
            os.mkdir(directory)

    # List all files that need to be compressed.
    all_files = []
    for f in os.listdir(TEMP_DIR):
        n = int(f.split('.')[0])
        all_files.append(os.path.join(TEMP_DIR,f))
    # Sort by the README index.
    all_files.sort(key = lambda p: get_n(p))

    # Manually increment starting index.
    first_n = get_n(all_files[0])
    while start + inc <= first_n:
        start += inc
    end = start + inc

    print 'Starting at', start
    print 'Number of files', len(all_files)
    time.sleep(5)

    f_index = 0
    while f_index < len(all_files):

        # Find files in the current range.
        files_to_compress = []
        for i in range(f_index, len(all_files)): # Prevents index from going out of bounds.
            # Increment index if it is in the current range.
            if get_n(all_files[f_index]) >= start and get_n(all_files[f_index]) < end:
                files_to_compress.append(all_files[f_index])
                f_index += 1

        # Check if there this range has work.
        if len(files_to_compress) > 0:
            
            z_dir = os.path.join(RAW, str(int(end / 1000000) + 1) + 'm')
            z_name = str(end) + '.7z'

            # Create 7z command.
            command = '7z a ' + os.path.join(z_dir,z_name)
            for i in range(0,5):
                # Include ./ before file name to not include the temporary directory
                # name in the archive.
                command += ' .' + os.path.sep
                # * to ignore the hundred's place in file name.
                command += os.path.join(TEMP_DIR,str(start/1000+i) + '*.md')
            os.system(command)

        start += inc
        end = start + inc
