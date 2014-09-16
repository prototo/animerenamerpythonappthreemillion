from lib.models import *
from lib.anidb.animeinfo import Anime
from lib.anidb.endpoints import *
from os.path import isfile
import config

def indexFile(path):
    if not isfile(path):
        return False

    if AuthRequest().doRequest():
        response = FileRequest(path).doRequest()
        print(response)
        LogoutRequest().doRequest()
