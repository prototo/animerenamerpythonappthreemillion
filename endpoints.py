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
    connection.session = data["session"]
    return data

# logout of the current session
class LogoutRequest(Request):
  location = "LOGOUT"


"""
  ANIME DATA
"""

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
    # aid|crc32|quality|codec|bitrate|resolution|description|mylist state
    "fmask": "40088E1080",
    # total episodes|romaji name|english name|ep number|english title|romaji title|group
    "amask": "80A0E080"
  }
  zip_params = [
    "fid",  # fid is always sent
    "aid", "crc", "quality", "codec", "bitrate", "res", "desc", "mylist_state",  # fmask
    "epcount", "romaji_name", "name", "epno", "title", "romaji_title", "group" # amask
  ]

  def __init__(self, filename):
    # set the size and hash of the file in the request parameters
    self.params["size"] = os.path.getsize(filename)
    self.params["ed2k"] = ed2k.hash(filename)

