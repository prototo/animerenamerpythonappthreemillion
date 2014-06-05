from config import *
from urllib.parse import urlencode
from urllib.request import urlretrieve
import httplib2
import os.path
import xml.etree.ElementTree as etree
import index
import datetime

def get_date(str):
	try:
		d = datetime.datetime.strptime(str, '%Y-%m-%d')
		return d
	except:
		return None

class Anime:
	xml = None #raw utf-8 string
	root = None #root element
	aid = None

	def __init__(self, aid):
		self.aid = aid
		self.xml = AnimeFetcher(aid).getXML()

		# no XML? AnimeFetcher failed but couldn't do anything about it due to poor design
		# raise noSuchAnimeError somewhere?
		if self.xml is None:
			return None
		self.root = etree.fromstring(self.xml)

		if self.index_anime():
			self.index_episodes()

	def getType(self):
		type = self.root.find('type')
		return self.elementText(type)

	def getEpisodecount(self):
		episodecount = self.root.find('episodecount')
		return self.elementText(episodecount)

	def getStartdate(self):
		startdate = self.root.find('startdate')
		return self.elementText(startdate)

	def getEndDate(self):
		enddate = self.root.find('enddate')
		return self.elementText(enddate)

	def getTitle(self):
		dict = {}
		titles = self.root.find('titles')
		if titles is None:
			return None
		for title in titles:
			dict[title.get('{http://www.w3.org/XML/1998/namespace}lang')] = title.text
		return dict

	def getDescription(self):
		description = self.root.find('description')
		return self.elementText(description)

	# images pulled to image_store/aid.jpg
	def getPicture(self):
		path = image_store + str(self.aid) + '.jpg'

		# check locally first
		if os.path.isfile(path):
			print("Picture: we got it")
			return path

		# gonna have to be the internets
		base = 'http://img7.anidb.net/pics/anime/'
		location = self.root.find('picture')

		if location is None:
			return None
		else:
			try:
				#print('urllib.request.urlretrieve({0}{1})'.format(base, location.text))
				path, headers = urlretrieve(base+location.text, path)
				return path
			except:
				print("Who knows... No pictures though")
				return None


	def getCategories(self):
		#dict = {}
		list = []
		categories = self.root.find('categories')
		if categories is None:
			return None
		for category in categories:
			name = category.find('name')
			#desc = category.find('description')
			#dict[name.text] = category.texts
			list.append(name.text)
		return list

	# build a dictionary of {ep { id, airdate, length, titles {lang, lang 2}}}
	def getEpisodes(self):
		a = {}
		episodes = self.root.find('episodes')
		if episodes is None:
			return None
		for episode in episodes:
			epno = episode.find('epno').text
			a[epno] = {}
			dict = {}
			if episode.find('epno').get('type') == '1':
				a[epno]['id'] = episode.get('id')
				#print(episode.get('id'))
				airdate = episode.find('airdate')
				a[epno]['airdate'] = airdate.text if airdate != None else None
				#sprint(episode.find('airdate').text)
				a[epno]['length'] = episode.find('length').text
				#print(episode.find('length').text)
				titles = episode.findall('title')
				for title in titles:
					dict[title.get('{http://www.w3.org/XML/1998/namespace}lang')] = title.text
				a[epno]['title'] = dict

		return a

	#
	def elementText(self, element):
		if element is None:
			return None
		else:
			return element.text

	# index epiosdes from HTTP API XML data
	def index_episodes(self):
		episodes = self.getEpisodes()

		for key in list(episodes.keys()):
			episode = episodes.get(key, None)
			if not episode:
				continue

			titles = episode.get('title')
			aired_date = get_date(episode.get('airdate', None))

			index.add_episode(
				id=episode.get('id'), aid=self.aid,
				epno=key,
				title=titles.get('en', None),
				title_ro=titles.get('x-jat', None),
				title_jp=titles.get('ja', None),
				aired_date=aired_date
			)

		return True

	# index anime from HTTP API XML data
	def index_anime(self):
		# if we've already indexed this anime, return
		# TODO: Just load this object from that data we've already stored rather than doing the API request
		if index.get_anime(self.aid) != None:
			return False

		names = self.getTitle()
		name = names.get('en', None)
		name_ro = names.get('x-jat', None)
		name_jp = names.get('ja', None)
		start_date = get_date(self.getStartdate())
		end_date = get_date(self.getEndDate())

		index.add_anime(
			id=self.aid, name=name, name_ro=name_ro, name_jp=name_jp,
			episode_count=self.getEpisodecount(),
			description=self.getDescription(),
			picture='', # self.getPicture(),
			start_date=start_date,
			end_date=end_date
		)

		return True

class AnimeFetcher:
	aid = None
	xml = None
	root = None
	path = None

	def __init__(self, aid):
		self.aid = aid
		self.path = data_store + str(aid) + ".xml"
		self.loadXML()

	# return utf-8 string representation
	def getXML(self):
		return self.xml

	# if aid.xml present read into self.xml, else DOWNLOAD
	def loadXML(self):
		if os.path.isfile(self.path):
			print("Found it!")
			with open(self.path, mode='r', encoding='utf-8') as file:
				self.xml = file.read()
		else:
			print("Nope.  Downloading")
			self.downloadXML(self.getAddress())

		# if at this point self.xml isn't set, something failed

	# create/overwrite aid.xml
	def storeXML(self, xml):
		with open(self.path, mode='w', encoding='utf-8') as file:
			file.write(self.xml)
		print("Stored")

	# download contents of specified url, response returned as string
	# content is bytes
	def downloadXML(self, url):
		h = httplib2.Http('.cache')
		response, content = h.request(url)
		# api responds with a single <error> element incase of error
		temp_xml = content.decode()
		root = etree.fromstring(temp_xml)
		if root.tag == 'error':
			print("That didn't work: " + root.text)
			return None

		self.xml = temp_xml
		self.storeXML(self.xml)

	# return request url as string
	def getAddress(self):
		base = "http://api.anidb.net:9001/httpapi?"
		params = {
			"client": HTTP_CLIENT_NAME,
			"clientver": HTTP_CLIENT_VERSION,
			"protover": HTTP_PROTOVER,
			"request": "anime",
			"aid": self.aid
		}
		request = "{0}{1}".format(base, urlencode(params))

		print("Full request: " + request)
		return request

