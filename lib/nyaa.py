import urllib.request
from urllib.parse import quote
import xml.etree.ElementTree as ET
from uuid import uuid4
from config import torrent_watch_dir as watch_dir
import os
import re
import lib.index as index

# &cats=1_37 is for english-translated torrents only
base_uri = 'http://www.nyaa.se/?page=rss&cats=1_37&term='
response_cache = {}

class Nyaa:
    names = []
    group = None
    quality = None

    title_regex = '{group}.*?{name}.*?( {epno}|{epno})'

    def __init__(self, aid):
        global response_cache
        self.response_cache = response_cache
        self.anime = index.get_anime(aid)

        # build the response cache of search results for all the names we have
        self.get_results()

    # do a search for the set anime, group and quality
    def get_results(self):
        if not self.anime:
            return False

        print("Grabbing nyaa results for", self.anime)
        for group_status in self.anime.groups:
            group = group_status.group.name

            names = self.anime.get_names()
            for name in names:
                # build the search request uri
                search_uri = quote(" ").join([
                    base_uri,
                    quote(group),
                    quote(name)
                ])

                identifier = ".".join([group, name])
                if not identifier in self.response_cache:
                    # do the request, cache and return the response
                    with urllib.request.urlopen(search_uri) as response:
                        data = response.read()
                        self.response_cache[identifier] = data

    # find the torrent for a single episode of this anime
    # TODO: could probably split this up some how
    def find_episode(self, epno):
        if (epno < 10):
            epno = "0" + str(epno)

        torrents = []
        for group_status in self.anime.groups:
            group = group_status.group.name

            names = self.anime.get_names()
            for name in names:
                identifier = ".".join([group, name])

                # find the response data for this name
                data = self.response_cache.get(identifier, None)
                if not data:
                    continue

                # set up the torrent title matching regex
                regex = "".join([re.escape(group), "[^\]]*?\].*?", re.escape(name), "[^\[]*?", re.escape(str(epno))])
                # regex = re.sub('[\s|\-|\_|\.]', '.*?', regex)
                p = re.compile(regex, re.IGNORECASE)

                # get the items in the search results
                root = ET.fromstring(data)
                channel = root.find('channel')
                items = channel.findall('item')

                if items:
                    for item in items:
                        title = item.find('title').text
                        link = item.find('link').text

                        # returns None if it doesn't match anywhere
                        if p.search(title):
                            # if the regex matches on the title, it's probably right!
                            # print(link, title)
                            torrents.append((link, title))

        # sort everything by title
        torrents = sorted(torrents, key=lambda item: item[1])
        return torrents

    # expect episodes to be a list of ints
    # TODO: decide if list of ints is actually a good way to do this
    def find_episodes(self, episodes):
        # call find torrent on all the episode numbers given
        torrents = []
        for episode in episodes:
            torrent = self.find_episode(episode.epno)
            if torrent[0]:
                torrent = (torrent[0], torrent[1], episode.id)
                torrents.append(torrent)

        # could be empty, let client worry about that
        return torrents

    # generate a unique id for the torrent filename if one hasn't been given
    @classmethod
    def download_torrent(cls, link, filename=None, eid=None):
        if not filename:
            filename = str(uuid4())
        elif ' ' in filename:
            filename = filename.replace(' ', '_')

        filename += ".torrent"
        filepath = os.path.join(watch_dir, filename)
        print("downloading",link,"to",filepath)

        # download the torrent
        urllib.request.urlretrieve(link, filepath)

        # add this episode to the downloads table
        if eid:
            index.add_download(eid=eid)

    # expects the return format of self.find_torrents
    def download_torrents(self, torrents):
        for torrent in torrents:
            self.download_torrent(*torrent)
