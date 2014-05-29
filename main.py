#!/bin/env python

import sys, os, re
import config
from endpoints import *
import index

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
  except OSError as e:
    print(e)
    pass  # should probably actually do something here

# request the episode data for the given file
def getEpisodeData(filepath):
  epno_regex = r"[ _-](\d{1,2})[ _-v]"

  if index.file_path_exists(filepath):
    print("Previously indexed", filepath)
    return False

  if os.path.isfile(filepath):
    file_request = FileRequest(filepath)
    file_data = file_request.doRequest()

    if not file_data:
      print("Couldn't retrieve data for", filepath)
      return False

    data = file_data.copy()
    data.update({ 'path' : filepath })
    index.add_file(**data)

    data['id'] = data.get('eid', None)
    index.add_episode(**data)

    data['id'] = data.get('aid', None)
    index.add_anime(**data)

    print("")

    # data = request.doRequest()
    return file_data

# walk down the given directory and get data for any episodes found
def parseDirectory(dirpath):
  indexable = ['.avi', '.mkv', '.mp4']

  for (path, dirs, files) in os.walk(dirpath):
    # recurse through all the subdirs
    for dir in dirs:
      dirpath = path + dir
      parseDirectory(dirpath)

    name = None
    aid = None
    for file in files:
      extension = os.path.splitext(file)[1]
      if not extension in indexable:
        continue

      filepath = os.path.join(path, file)

      data = getEpisodeData(filepath)
      if not data:
        continue

      # bail out here because I'm irresponsible and can't be bothered to tidy this up
      continue

      # extract and normalise the data
      if not aid:
        aid = data.get('aid', None)

      if not name:
        name = data.get('romaji_name') or data.get('name')
        if not name:
          print("Didn't find anime name")
          break

      epno = data.get('epno')
      title = data.get('title') or data.get('romaji_title')

      # if we've got everything we need rename the file
      if name and epno and title:
        pass
        # renameEpisode(filepath, name, data['epno'], data['title'])

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

  parseDirectory(dirpath)

  # finally logout
  logout.doRequest()
  print("End")

