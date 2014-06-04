import urllib.request
import gzip
import config
import os
import xml.etree.ElementTree as ET
from difflib import get_close_matches as closest

titles_file_url = "http://anidb.net/api/anime-titles.xml.gz"
file_location = os.path.join(config.data_store, '.anime-titles.xml')

def download_titles_file():
    # truncate the file if it already exists
    with open(file_location, 'w') as output_file:
        pass

    # pull the new version, decompress it and write it out to the file
    with open(file_location, 'a') as output_file:
        print("open")
        with urllib.request.urlopen(titles_file_url) as response:
            print("url open")
            with gzip.GzipFile(fileobj=response) as uncompressed:
                print("starting")
                while 1:
                    data = uncompressed.read(1024)
                    print(data)
                    if not data:
                        break
                    output_file.write(data.decode('utf-8'))

def get_title_data():
    tree = ET.parse(file_location)
    root = tree.getroot()
    data = {}

    for anime in root:
        aid = anime.attrib['aid']
        for title in anime:
            key = title.text
            data[key] = aid

    return data

# TODO: this needs some work...
def search(term, n=50):
    data = get_title_data()
    best = closest(term, data.keys(), n)
    results = [ (key, data[key]) for key in best ]
    return results

