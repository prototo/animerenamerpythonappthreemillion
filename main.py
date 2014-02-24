#!/bin/env python

import sys, os, re
import config
from endpoints import *

store = ""
try:
  store = config.store
except:
  pass

# could just pass in the data block and have a format string for file name
def renameEpisode(filepath, name, epno, title):
  if len(str(epno)) == 1:
    epno = "0" + str(epno)
  filename, extension = os.path.splitext(filepath)

  # replace any forward slash with backslashes for the file names
  new_filename = "{0} - {1} {2}{3}".format(name, epno, title, extension).replace("/", "\\")
  new_filepath = os.sep.join([store, name, new_filename])

  try:
    os.renames(filepath, new_filepath)
    print("{0} => {1}".format(os.path.basename(filepath), os.path.basename(new_filepath)))
  except OSError:
    pass  # should probably actually do something here

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
    if len(dirs):
      print("Found folders in " + path + ", not risking it")
      continue

    name = None
    aid = None
    for file in files:
      filepath = path + file
      data = getEpisodeData(filepath, aid)

      # extract and normalise the data
      if not aid:
        aid = data.get('aid', None)

      if not name:
        name = data.get('name') or data.get('romaji_name')
        if not name:
          print("Didn't find anime name")
          print(data)
          break

      epno = data.get('epno')
      title = data.get('title') or data.get('romaji_title')

      # if we've got everything we need rename the file
      if name and epno and title:
        renameEpisode(filepath, name, data['epno'], data['title'])

    # delete the current dir if it's empty
    try:
      os.rmdir(path)
    except OSError:
      pass

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
    print("Unexpected error:", sys.exc_info()[0])
    exit(1)

  # finally logout
  logout.doRequest()
  print("End")

