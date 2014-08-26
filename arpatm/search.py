import urllib.request
import gzip
import config
import os
import os.path
import xml.etree.ElementTree as ET
from time import time

titles_file_url = "http://anidb.net/api/anime-titles.xml.gz"
file_location = os.path.join(config.data_store, '.anime-titles.xml')

def getTitlesFileAge():
    if os.path.isfile(file_location):
        age = os.path.getmtime(file_location)
        age = (time() - age) / 60 / 60 / 24
        return age / 60 / 60 / 24   # return in days
    return 9999

def downloadTitlesFile():
    # if we don't need to download a new copy just return
    if getTitlesFileAge() < 1:
        return True

    print("Downloading titles file")
    # pull the new version, decompress it and write it out to the file
    urllib.request.urlretrieve(titles_file_url, file_location)
    with gzip.open(file_location) as data:
        titles = data.read().decode()
        with open(file_location, 'w') as output_file:
            output_file.write(titles)

def getTitleData():
    downloadTitlesFile()

    tree = ET.parse(file_location)
    root = tree.getroot()
    data = []

    for anime in root:
        aid = anime.attrib['aid']
        item = {'id': aid, 'main': '', 'titles': []}
        for title in anime:
            lang = title.get('{http://www.w3.org/XML/1998/namespace}lang')
            type = title.get('type')
            if type == 'main':
                item['main'] = title.text
            if lang in ['en', 'ja', 'x-jat']:
                item['titles'].append(title.text)
        data.append(item)

    return sorted(data, key=lambda x: x['main'])

def search(term):
    data = getTitleData()
    tokens = term.lower().split(' ')
    return list(filter(lambda anime: any(all(token in title.lower() for token in tokens) for title in anime['titles']), data))

