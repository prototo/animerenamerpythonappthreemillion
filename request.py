#!/bin/env python

from config import *
import socket
import re
import urllib
import connection
from time import time, sleep

# The request class that all the other requests can inherit
class Request:
  location = ""
  params = {}
  response_regex = None
  requires_session = True # most requests do

  # return the location for this request in bytes format
  def getLocation(self):
    if (connection.session):
      self.params['s'] = connection.session
    params = urllib.urlencode(self.params)
    location = "{0} {1}".format(self.location, params)
    print("Sending request to: " + location)
    return bytes(location)

  # send the request and return the data we get back
  # this method is blocking
  def doRequest(self):
    location = self.getLocation()
    while (time() - connection.last_request) < 2:
      sleep(1)
    connection.sock.sendto(location, (API_ADDR, API_PORT))
    data, addr = connection.sock.recvfrom(1400)
    data = data.decode("utf-8")
    print("Got: " + data)

    # update the last_request time
    connection.last_request = time()

    # if we have a regex get the dictionary of useful values
    if self.response_regex:
      return self.matchResponse(data)
    return data

  # gets a dictionary of named groups
  def matchResponse(self, data):
    group = re.match(self.response_regex, data)
    if not group:
      return None
    return group.groupdict()

    connection.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.sock.bind(('', CLIENT_PORT))
