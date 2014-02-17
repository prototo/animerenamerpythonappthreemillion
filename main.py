#!/bin/env python

from endpoints import *

auth = AuthRequest()
logout = LogoutRequest()

res = auth.doRequest()
if int(res['status']) in (200, 201):
  session = res['session']
  logout.doRequest()
