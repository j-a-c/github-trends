import os

from sorted_directory_iterator import SortedDirectoryIterator

def get_index(iterator, index):
    """
    Returns the item at the specified index in the iterator.
    """
    counter = 0
    for item in iterator:
        if counter == index:
            return item
            break
        counter += 1
    return None

if __name__ == '__main__':

    # The top level folder containing the urls.
    URL_DIRECTORY = os.path.join('..', 'urls', 'raw')
    # The top level folder containing the metdata.
    METADATA_DIRECTORY = 'metadata'

    # Construct iterators over our data.
    # These iterators have different length since we do only have metadata for
    # a subset of the URLs. But as you will see later, we can map a URL to
    # its metadata and READMEs still.
    url_iterator = SortedDirectoryIterator(URL_DIRECTORY)
    metadata_iterator = SortedDirectoryIterator(METADATA_DIRECTORY)

    # Print the url at index target_url_index.
    target_url_index = 10000
    print get_index(url_iterator, target_url_index)
    print get_index(url_iterator, target_url_index)

    # Print the metadata at index target_metadata_index.
    target_metadata_index = 100
    print get_index(metadata_iterator, target_metadata_index)
    print get_index(metadata_iterator, target_metadata_index)
        
