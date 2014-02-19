#!/bin/env python

import sys
import os
import re
from endpoints import *

# request the episode data for the given file
def getEpisodeData(filepath, aid = None):
  epno_regex = r"[ _-](\d{1,2})[ _-v]"
  if os.path.isfile(filepath):
    request = None
    if aid:
      try:
        epno = re.search(epno_regex, os.path.basename(filepath)).group(1)
        request = EpisodeRequest(aid, epno)
      except:
        request = FileRequest(filepath)
    else:
      request = FileRequest(filepath)
    data = request.doRequest()
    return data

# walk down the given directory and get data for any episodes found
def parseDirectory(dirpath):
  for (path, dirs, files) in os.walk(dirpath):
    name = None
    aid = None
    for file in files:
      filepath = os.sep.join([path, file])
      data = getEpisodeData(filepath, aid)

      # extract and normalise the data
      if 'aid' in data:
        aid = data['aid']

      if 'name' in data:
        name = data['name']
      elif name:
        data['name'] = name

      # show what we got
      print("{name}: {epno} {title}".format(**data))

# filepath
dirpath = sys.argv[1]
if not os.path.exists(dirpath) or not os.path.isdir(dirpath):
  print(filename + " doesn't exist, need an actual directory plz")
  exit(0)

# request objects
auth = AuthRequest()
logout = LogoutRequest()

# do some shit
res = auth.doRequest()
if int(res['status']) in (200, 201):
  print("Logged in with session " + res['session'])

  try:
    # parse the directory for ANIMEZ
    parseDirectory(dirpath)
  except:
    # if something breaks logout
    logout.doRequest()
    print("Errors happened")
    print "Unexpected error:", sys.exc_info()[0]
    exit(1)

  # finally logout
  logout.doRequest()
  print("End")

