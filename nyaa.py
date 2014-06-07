import urllib.request
from urllib.parse import quote
import xml.etree.ElementTree as ET
from uuid import uuid4
from config import torrent_watch_dir as watch_dir
import os
import re

base_uri = 'http://www.nyaa.se/?page=rss&term='

class Nyaa:
    response_cache = {}
    names = []
    group = None
    quality = None

    title_regex = '{group}.*?{name}.*?( {epno}|{epno} ).*?{quality}'

    def __init__(self, names, group = 'horriblesubs', quality = 720):
        self.names = names
        self.group = group
        self.quality = quality

        # build the response cache of search results for all the names we have
        self.get_results()

    # do a search for the set anime, group and quality
    def get_results(self):
        if not len(self.names):
            return False

        for name in self.names:
            # if we've already requested this name and got a response, skip it
            if not name in self.response_cache:
                # build the search request uri
                search_uri = quote(" ").join([
                    base_uri,
                    self.group,
                    quote(name),
                    str(self.quality)
                ])

                # do the request, cache and return the response
                with urllib.request.urlopen(search_uri) as response:
                    data = response.read()
                    self.response_cache[name] = data

    # find the torrent for a single episode of this anime
    # TODO: could probably split this up some how
    def find_episode(self, epno):
        if (epno < 10):
            epno = "0" + str(epno)

        for name in self.names:
            # find the response data for this name
            data = self.response_cache[name]
            if not data:
                continue

            # set up the torrent title matching regex
            name_tokens = re.split('[\s|\-|\_|\.]', name)
            regex = self.title_regex.format(
                group = self.group,
                name = '.*?'.join(name_tokens),
                epno = str(epno),
                quality = str(self.quality)
            )
            regex = re.compile(regex, re.IGNORECASE)

            # get the items in the search results
            root = ET.fromstring(data)
            channel = root.find('channel')
            items = channel.findall('item')

            if items:
                for item in items:
                    title = item.find('title').text
                    link = item.find('link').text

                    # returns None if it doesn't match anywhere
                    if regex.search(title):
                        # if the regex matches on the title, it's probably right!
                        return (link, title)

        # didn't find anything for any of the set titles, return None
        return (None, None)

    # expect episodes to be a list of ints
    # TODO: decide if list of ints is actually a good way to do this
    def find_episodes(self, episodes):
        # call find torrent on all the episode numbers given
        torrents = map(self.find_episode, episodes)
        torrents = [ t for t in torrents if t[0] ]

        # could be empty, let client worry about that
        return torrents

    # generate a unique id for the torrent filename if one hasn't been given
    def download_torrent(self, link, filename=str(uuid4())):
        if ' ' in filename:
            filename = filename.replace(' ', '_')
        filename = filename + ".torrent"
        filepath = os.path.join(watch_dir, filename)
        print ("downloading",link,"to",filepath)

        urllib.request.urlretrieve(link, filepath)

    # expects the return format of self.find_torrents
    def download_torrents(self, torrents):
        for torrent in torrents:
            self.download_torrent(*torrent)
