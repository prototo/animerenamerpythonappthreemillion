#!/bin/env python

import os
import connection
import ed2k
from config import *
from request import Request

"""
  AUTHENTICATION
"""

# The auth request class
class AuthRequest(Request):
  location = "AUTH"
  params = {
    "user": username,
    "pass": password,
    "protover": PROTOVER,
    "client": CLIENT_NAME,
    "clientver": CLIENT_VERSION
  }
  response_regex = r"^(?P<status>\d*) (?P<session>\w*)"

  def doRequest(self):
    data = Request.doRequest(self)
    if data:
      connection.session = data["session"]
      return data
    return None

# logout of the current session
class LogoutRequest(Request):
  location = "LOGOUT"


"""
  ANIME DATA
"""
#get anime data by aid
class AnimeRequest(Request):
  location = "ANIME"
  amask = "b2208400000000"
  zip_params = [
      "aid", "year", "type", "category", "eng_name", "episodes", "url"
  ]

  def __init__(self, aid):
    self.params['aid'] = aid
    self.params['amask'] = self.amask

# get episode data by aid and ep no
class EpisodeRequest(Request):
  location = "EPISODE"
  zip_params = [
    "eid", "aid", "length", "rating", "votes",
    "epno", "title", "romaji_title", "kanji_title", "aired", "type"
  ]

  def __init__(self, aid, episode_number):
    self.params['aid'] = aid
    self.params['epno'] = episode_number

# get data by file hash
class FileRequest(Request):
  location = "FILE"
  params = {
    # aid|eid|ed2k|quality|codec|bitrate|resolution|description|mylist state
    "fmask": "60408E1080",
    # total episodes|romaji name|kanji name|english name|ep number|english title|romaji title|kanji title|group
    "amask": "80E0F080"
  }
  zip_params = [
    "fid",  # fid is always sent
    "aid", "eid", "ed2k", "quality", "codec", "bitrate", "resolution", "description", "mylist_state",  # fmask
    "episode_count", "name_ro", "name_jp", "name", "epno", "title", "title_ro", "title_jp", "group" # amask
  ]

  def __init__(self, filename):
    # set the size and hash of the file in the request parameters
    self.params["size"] = os.path.getsize(filename)
    self.params["ed2k"] = ed2k.hash(filename)
