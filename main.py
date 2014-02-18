#!/bin/env python

import sys
import os
from endpoints import *

# filepath
filename = sys.argv[1]
if not os.path.exists(filename):
  print(filename + " doesn't exist, need an actual file plz")
  exit(0)

# request objects
auth = AuthRequest()
logout = LogoutRequest()
file = FileRequest(filename)

# do some shit
res = auth.doRequest()
if int(res['status']) in (200, 201):
  file.doRequest()
  logout.doRequest()
