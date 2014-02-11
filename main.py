#!/bin/env python

import socket

# api location
API_ADDR = 'api.anidb.net'
API_PORT = 9000

# various data for api calls
PROTOVER = 3  # this is the api version (I think)
CLIENT_NAME = 'ARPATM'
CLIENT_VERSION = 0
CLIENT_PORT = 1024  # don't know why I chose this

# fake user data to try authenticating with
uname = 'prototo'
upass = 'prototo'

# make a fake auth request
msg = "AUTH user=%s&pass=%s&protover=%s&client=%s&clientver=%s" % (uname, upass, PROTOVER, CLIENT_NAME, CLIENT_VERSION)
print("sending the following message:\n", msg)

# make the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# the socket binds locally to CLIENT_PORT to listen for responses
sock.bind(('', CLIENT_PORT))

# send the message
# everything sending and receiving on the UDP socket is in a bytes format
# so we have to convert to/from and sending/receiving
sock.sendto(bytes(msg, "utf-8"), (API_ADDR, API_PORT))

# wait infinitely for something to come back on our socket and
# get put in the data variable
data = False
while not data:
  data, addr = sock.recvfrom(1400)  # buffer size of 1400 bytes
  data = data.decode("utf-8")
  print("got this back:\n", data)

# yey
exit(0)
