from urllib.request import urlopen, urlretrieve
from urllib.parse import quote
import os.path
import xml.etree.ElementTree as ET
from random import randint
from config import TVDB_KEY, data_store, image_store

mirrors_file = os.path.join(data_store, '.mirrors.xml')
mirrors_path = 'http://thetvdb.com/api/{key}/mirrors.xml'.format(key=TVDB_KEY)
series_path = '{mirror}/api/GetSeries.php?seriesname={series}'
banners_data_path = '{mirror}/api/{key}/series/{id}/banners.xml'
banner_image_path = '{mirror}/banners/{bannerpath}'

tvdb_data_store = os.path.join(data_store, 'tvdb')
tvdb_image_store = os.path.join(image_store, 'tvdb')

# there only seems to ever be on mirror returned with typemask of 7 but just in case
# http://www.thetvdb.com/wiki/index.php?title=API:mirrors.xml
# xml_masks = [ 1, 3, 5, 7 ]
xml_masks = [ 7 ]   # only mirrors with everything cause we need that zip

# this is NOT recursive
def element_to_dict(element):
    if not element:
        return
    data = {}
    for item in list(element):
        data[item.tag.lower()] = item.text
    return data

class TVDB:
    mirrors = []
    mirror = None

    def __init__(self):
        self.get_mirrors()

    def get_mirrors(self):
        # if we don't have a cache of the mirrors file go get it
        if not os.path.isfile(mirrors_file):
            urlretrieve(mirrors_path, mirrors_file)

        # parse the mirrors file and get all the suitable mirrors
        root = ET.parse(mirrors_file).getroot()
        for item in root.iter('Mirror'):
            mirror = element_to_dict(item)
            if int(mirror['typemask']) in xml_masks:
                self.mirrors.append(mirror)

        # choose a mirror from the loaded file for future ops
        self.mirror = self.random_mirror()

    # if we have mirrors find a random one and return the path
    def random_mirror(self):
        length = len(self.mirrors)
        if length:
            if length == 1:
                return self.mirrors[0]['mirrorpath']
            return self.mirrors(randint(0, length - 1))['mirrorpath']
        return None

    def get_series(self, title):
        mirror = self.random_mirror()
        if not mirror:
            return False

        path = series_path.format(mirror=mirror, series=quote(title))
        data = None
        with urlopen(path) as response:
            data = response.read()

        root = ET.fromstring(data)
        series = root.find('Series')
        series = element_to_dict(series)

        return series

    def get_series_banners(self, title, type):
        series = self.get_series(title)
        if not series:
            return None

        series_id = series['seriesid']
        banners_file = os.path.join(data_store, 'banners_' + series_id + '.xml')

        if not os.path.isfile(banners_file):
            path = banners_data_path.format(mirror = self.mirror, key = TVDB_KEY, id = series_id)
            urlretrieve(path, banners_file)

        # series_image_dir = os.path.join(tvdb_image_store, series_id)
        # if not os.path.isdir(series_image_dir):
        #     os.makedirs(series_image_dir)

        root = ET.parse(banners_file).getroot()
        banners = []
        for item in root.iter('Banner'):
            banner = element_to_dict(item)
            if type and banner['bannertype'] != type:
                continue
            banners.append(banner)

        return banners

    def get_series_banner(self, title, type):
        banners = self.get_series_banners(title, type)
        if banners and len(banners):
            # just take the first (FOR NOW)
            banner = banners[0]
            banner_path = banner_image_path.format(mirror = self.mirror, bannerpath = banner['bannerpath'])
            banner_ext = os.path.splitext(banner_path)[1]
            banner_file_name = banner['id'] + banner_ext
            # banner_file = os.path.join(tvdb_image_store, banner_file_name)
            banner_file = os.path.join(image_store, banner_file_name)
            if not os.path.isfile(banner_file):
                urlretrieve(banner_path, banner_file)
            return banner_file_name

        return None

    def get_fanart(self, title):
        return self.get_series_banner(title, 'fanart')

    def get_poster(self, title):
        return self.get_series_banner(title, 'poster')
