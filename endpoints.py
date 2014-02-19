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
    "epno", "title", "kanji", "aired", "type"
  ]

  def __init__(self, aid, episode_number):
    self.params['aid'] = aid
    self.params['epno'] = episode_number

# get data by file hash
class FileRequest(Request):
  location = "FILE"
  params = {
    # aid|crc32|resolution|description|mylist state
    "fmask": "4008021080",
    # total episodes|english name|episode number|episode name|group name
    "amask": "8020C080"
  }
  zip_params = [
    "fid",  # fid is always sent
    "aid", "crc", "res", "desc", "mylist",  # fmask
    "episodes", "name", "epno", "title", "group"  # amask
  ]

  def __init__(self, filename):
    # set the size and hash of the file in the request parameters
    self.params["size"] = os.path.getsize(filename)
    self.params["ed2k"] = ed2k.hash(filename)

