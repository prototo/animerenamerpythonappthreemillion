#!/bin/env python

import socket
from config import CLIENT_PORT
from time import time

# setup the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', CLIENT_PORT))

# session string
session = None

# last request time
last_request = time()

