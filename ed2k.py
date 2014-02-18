#!/bin/env python

import hashlib

def hash(filename, chunk_size=9500)
  # the ed2k hash object
  ed2k_hash = hashlib.new("md4")

  with open(filename, "r") as f:
    while True:
      # read a chunk_size chunk of the file
      chunk = f.read(1024 * chunk_size)
      if chunk:
        # calculate the md4 for the chunk and update the ed2k hash
        hash = hashlib.new("md4", chunk).hexdigest()
        ed2k_hash.update(hash)
      else:
        break

  # return the ed2k hash string
  return ed2k_hash.hexdigest()
