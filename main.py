#!/bin/env python

import socket
import re
from time import time, sleep

# api location
API_ADDR = 'api.anidb.net'
API_PORT = 9000

# various data for api calls
PROTOVER = 3  # this is the api version (I think)
CLIENT_NAME = 'arpatm'
CLIENT_VERSION = 0
CLIENT_PORT = 1024  # don't know why I chose this

# make the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# the socket binds locally to CLIENT_PORT to listen for responses
sock.bind(('', CLIENT_PORT))

# send the message
# everything sending and receiving on the UDP socket is in a bytes format
# so we have to convert to/from and sending/receiving
# sock.sendto(bytes(msg, "utf-8"), (API_ADDR, API_PORT))

# recvfrom should block and we're only waiting for one packet
# data, addr = sock.recvfrom(1400)  # buffer size of 1400 bytes
# data = data.decode("utf-8")

# shouldn't be sending more than one packet every two seconds
# so using this global for now to time them
last_request = round(time())

# The request class that all the other requests can inherit
class Request:
  location = ""
  partials = {}
  response_regex = None

  def __init__(self):
    return

  # return the location for this request in bytes format
  def getLocation(self, session=None):
    location = self.location.format(**self.partials)
    if (session):
      if (not " " in location):
        location = location + " "
      else:
        location = location + "&"
      location = location + "s=" + session
    print("Sending request to:\n" + location)
    return bytes(location, "utf-8")

  # send the request and return the data we get back
  # this method is blocking
  def doRequest(self, socket, session=None):
    global last_request
    location = self.getLocation(session)
    while round(time()) - last_request < 2:
      sleep(1)
    socket.sendto(location, (API_ADDR, API_PORT))
    data, addr = sock.recvfrom(1400)
    data = data.decode("utf-8")
    print("Got:\n" + data)

    # update the last_request time
    last_request = round(time())

    # if we have a regex get the dictionary of useful values
    if self.response_regex:
      return self.matchResponse(data)
    return data

  # gets a dictionary of named groups
  def matchResponse(self, data):
    group = re.match(self.response_regex, data)
    return group.groupdict()

# The auth request class
class AuthRequest(Request):
  location = "AUTH user={user}&pass={pass}&protover={protover}&client={client}&clientver={clientver}"
  partials = {
    'user': 'prototo',
    'pass': 'nope',
    'protover': PROTOVER,
    'client': CLIENT_NAME,
    'clientver': CLIENT_VERSION
  }
  response_regex = r"^(?P<status>\d*) (?P<session>\w*)"

# logout of the current session
class LogoutRequest(Request):
  location = "LOGOUT"

auth = AuthRequest()
logout = LogoutRequest()

res = auth.doRequest(sock)
if int(res['status']) in (200, 201):
  session = res['session']
  logout.doRequest(sock, session)
