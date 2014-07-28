#!/bin/env python

from config import *
import socket
import re
import connection
from urllib.parse import urlencode
from time import time, sleep

# The request class that all the other requests can inherit
class Request:
  location = ""
  params = {}
  response_regex = None
  zip_params = None
  requires_session = True # most requests do

  # return the location for this request in bytes format
  def getLocation(self):
    if (connection.session):
      self.params['s'] = connection.session
    params = urlencode(self.params)
    location = "{0} {1}".format(self.location, params)
    # print("Sending request to: " + location)
    return location

  # send the request and return the data we get back
  # this method is blocking
  def doRequest(self):
    location = self.getLocation()
    while (time() - connection.last_request) < 2:
      sleep(1)
    connection.sock.sendto(bytes(location.encode()), (API_ADDR, API_PORT))
    data = connection.sock.recv(1400)
    res = data.decode().strip().replace("\n", " ")
    # print("Got: " + res)

    # update the last_request time
    connection.last_request = time()

    # if we got anything other than a 2XX response return None
    if not self.wasSuccessful(res):
      print('unsuccessful response:', res)
      return None

    # if we have a regex get the dictionary of useful values
    if self.response_regex:
      return self.matchResponse(res)
    elif self.zip_params:
      return self.zipResponse(res)
    return res

  # gets a dictionary of named groups
  def matchResponse(self, res):
    group = re.match(self.response_regex, res)
    if not group:
      return None
    return group.groupdict()

  # zip the response data with the parameter names
  def zipResponse(self, res):
    # [2] should be the response data we want
    res = res.split(" ", 2)[2]
    res = res.split("|")
    # this replaces all the empty strings in res with None
    res = [val or None for val in res]
    data = dict(zip(self.zip_params, res))
    return data

  # check that the status code of the response was a 2XX
  def wasSuccessful(self, res):
    status = res.split(" ")[0]
    status = int(status)
    return status > 199 and status < 300
      
