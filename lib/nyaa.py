from urllib.request import urlopen
from urllib.parse import quote
import xml.etree.ElementTree as ET
from uuid import uuid4
from config import torrent_watch_dir as watch_dir
import os
import lib.models as index
import lib.anidb.animeinfo as animeinfo
from lib.transmission import add
import re

# &cats=1_37 is for english-translated torrents only
base_uri = 'http://www.nyaa.se/?page=rss&cats=1_37&offset={}&term={}'
response_cache = {}

class Nyaa:
    names = []
    group = None
    quality = None
    response = None

    title_regex = '{group}.*?{name}.*?( {epno}|{epno})'

    def __init__(self, aid):
        global response_cache

        self.aid = aid
        self.response_cache = response_cache

        # fetch the anime data if we don't have it yet
        animeinfo.Anime(aid)
        self.anime = index.Anime.get({'id': aid})

        # if we've got results for this aid cached, don't do the fetch
        if aid in response_cache:
            self.response = response_cache[aid]
        else:
            # build the response cache of search results for all the names we have
            self.get_results()

    # do a search for the set anime, group and quality
    def get_results(self):
        if not self.anime:
            return False

        print("Grabbing nyaa results for", self.anime)
        names = self.anime.get_names()
        results = set()
        for name in set(names):
            offset = 1
            while True:
                # build the search request uri
                search_uri = base_uri.format(str(offset), quote(name))

                # get and parse the response
                with urlopen(search_uri) as response:
                    data = response.read()
                    items = self.parse_response(data)

                # if items is false or empty, break from the while
                if not items:
                    break

                for item in items:
                    results.add(item)

                # increment the offset to get the next page of stuff
                offset += 1

        # cache the response list for this aid
        self.response_cache[self.aid] = results
        self.response = results

    def parse_response(self, data):
        root = ET.fromstring(data)
        channel = root.find('channel')
        items = channel.findall('item')

        # if theres no items in this response (eg, offset too high) return False
        if not items:
            return False

        # parse each XML 'item' into a tuple and return an array of them all
        return list(map(lambda x: (x.find('title').text, x.find('link').text), items))

    # find the torrent for a single episode of this anime
    def find_episode(self, epno):
        if (int(epno) < 10):
            epno = "0" + str(epno)

        torrents = []
        for item in self.response:
            title, link = item
            regexp = re.compile("(?:[ _-]{}|{}[ _-])".format(epno, epno))
            if regexp.search(title):
                torrents.append(item)

        # sort everything by title
        torrents = sorted(torrents, key=lambda item: item[0])
        return torrents

    # generate a unique id for the torrent filename if one hasn't been given
    @classmethod
    def download_torrent(cls, torrent, eid=None):
        title, link = torrent
        print("downloading", title)

        # WE NOW ONLY SUPPORT TRANSMISSION BECUASE GOD DAMN MAGNET LINKS UGH
        # add torrent to transmission
        add(link)

        # add this episode to the downloads table
        if eid:
            index.Download.add({'eid':eid})
