#!/bin/env python

from config import *
import re
import lib.anidb.connection as connection
from urllib.parse import urlencode
from time import time, sleep
from socket import timeout

timeout_lengths = [5, 30, 60, 120]

# The request class that all the other requests can inherit
class Request:
  location = ""
  params = {}
  response_regex = None
  zip_params = None
  requires_session = True # most requests do
  retry_attempts = 0

  # return the location for this request in bytes format
  def getLocation(self):
    if (connection.session):
      self.params['s'] = connection.session
    params = urlencode(self.params)
    location = "{0} {1}".format(self.location, params)
    # print("Sending request to: " + location)
    return location

  def getResponse(self):
    location = self.getLocation()
    print(location)

    while (time() - connection.last_request) < 2:
      sleep(1)

    try:
        connection.sock.settimeout(timeout_lengths[self.retry_attempts])
        connection.sock.sendto(bytes(location.encode()), (API_ADDR, API_PORT))
        data = connection.sock.recv(1400)
    except timeout:
        if self.retry_attempts >= (len(timeout_lengths) - 1):
            print("Couldn't complete " + location)
            return False
        self.retry_attempts = self.retry_attempts + 1
        print("Retrying...")
        return self.getResponse()
    except Exception:
        print("There was a problem with the socket request, the internet probably disappeared")
        return False

    data = data.decode().strip()

    # update the last_request time
    connection.last_request = time()

    return data

  # send the request and return the data we get back
  # this method is blocking
  def doRequest(self):
    if self.requires_session and not connection.session:
        raise Exception('This endpoint requires a session, perform an AuthRequest first')

    res = self.getResponse()

    if "\n" in res:
      (status, data) = res.split("\n", 1)
    else:
      status = data = res

    print(status)

    # if we got anything other than a 2XX response return None
    if not self.wasSuccessful(status):
      print('unsuccessful response:', status)
      return None

    # if we have a regex get the dictionary of useful values
    if self.response_regex:
      return self.matchResponse(data)
    elif self.zip_params:
      if "\n" in res:   # multi line return
        return self.zipMultipleLines(data)
      else:
        return self.zipResponse(data)
    return data

  # gets a dictionary of named groups
  def matchResponse(self, res):
    group = re.match(self.response_regex, res)
    if not group:
      return None
    return group.groupdict()

  def zipMultipleLines(self, res):
    return [self.zipResponse(line) for line in res.split("\n")]

  # zip the response data with the parameter names
  def zipResponse(self, res):
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
