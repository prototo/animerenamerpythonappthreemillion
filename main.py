#!/bin/env python

import sys
import os
from endpoints import *

import ed2k
testdir = "test/"

# request the episode data for the given file
def getEpisodeData(filepath):
  if os.path.isfile(filepath):  
    request = FileRequest(filepath)
    data = request.doRequest()
    print("{name}: {number} {title}".format(**data))

# walk down the given directory and get data for any episodes found
def parseDirectory(dirpath):
  for (path, dirs, files) in os.walk(dirpath):
    for file in files:
      filepath = os.sep.join([path, file])
      getEpisodeData(filepath)

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
  try:
    # parse the directory for ANIMEZ
    parseDirectory(dirpath)
  except:
    # if something breaks logout
    logout.doRequest()
    exit(1)

  # finally logout
  logout.doRequest()

