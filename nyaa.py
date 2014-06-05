import urllib.request
from urllib.parse import quote
import xml.etree.ElementTree as ET
from uuid import uuid4
from config import torrent_watch_dir as watch_dir
import os

base_uri = 'http://www.nyaa.se/?page=rss&term='

class Nyaa:
    def __init__(self):
        pass

    # horriblesubs is a placeholder, obviously won't work for everything
    def find_torrent(self, name, group='horriblesubs', quality=720, epno=1):
        if (epno < 10):
            epno = "0" + str(epno)
        search_uri = quote(" ").join([base_uri, quote(name), str(quality), quote(group), str(epno)])
        print("requesting", search_uri)
        with urllib.request.urlopen(search_uri) as response:
            data = response.read()
            return self.parse_response(data)

    def parse_response(self, response):
        root = ET.fromstring(response)
        channel = root.find('channel')
        item = channel.find('item')

        if item:
            title = item.find('title').text
            link = item.find('link').text
            print("found",title)
            return (title, link)

        return False

    # generate a unique id for the torrent filename if one hasn't been given
    def download_torrent(self, link, filename=str(uuid4())):
        if ' ' in filename:
            filename = filename.replace(' ', '_')
        filepath = os.path.join(watch_dir, filename)

        with urllib.request.urlopen(link) as response:
            with open(filepath, "w") as f:
                data = response.read()
                f.write(str(data))
