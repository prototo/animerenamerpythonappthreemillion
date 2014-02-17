#!/bin/env python

import connection
from config import *
from request import Request

# The auth request class
class AuthRequest(Request):
  location = "AUTH"
  params = {
    'user': username,
    'pass': password,
    'protover': PROTOVER,
    'client': CLIENT_NAME,
    'clientver': CLIENT_VERSION
  }
  response_regex = r"^(?P<status>\d*) (?P<session>\w*)"

  def doRequest(self):
    data = Request.doRequest(self)
    connection.session = data['session']
    return data

# logout of the current session
class LogoutRequest(Request):
  location = "LOGOUT"

