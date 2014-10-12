from lib.models import *
from lib.anidb.endpoints import *
from lib.anidb.animeinfo import Anime as AnimeInfo
import lib.anidb.ed2k as ed2k
import lib.anidb.connection as connection
from os.path import isfile, isdir, join, splitext, basename, getsize, dirname
from os import walk, listdir, rmdir, rename, mkdir
import config
import re

FILEFORMAT = "{epno} {title}"

def create_parent_dir(data):
    store = config.store
    new_dir_path = join(store, data.get('name'))
    if not isdir(new_dir_path):
        mkdir(new_dir_path)
    return new_dir_path

def rename_file(path, data):
    base, ext = splitext(path)
    parent_dir = create_parent_dir(data)
    data['title'] = re.sub('(?:\s*\/+\s*)+', ' ', data.get('title', ''))
    new_path = FILEFORMAT.format(**data) + ext
    new_path = join(parent_dir, new_path)

    if path == new_path:
        return path

    try:
        if isfile(new_path):
            hash_file(new_path)

        if isfile(new_path):
            raise Exception("File exists ({})".format(new_path))

        rename(path, new_path)
        print(" -> {}".format(new_path))

        old_dir = dirname(path)
        if not listdir(old_dir):
            print("Removing empty directory:", old_dir)
            rmdir(old_dir)
    except OSError as e:
        # something went wrong..!
        print('failed to move', e)
        return False
    except Exception as e:
        print(e)
        return False

    return new_path

def index_file(path, ed2k):
    if not isfile(path):
        return False

    # get the file endpoint response for this file
    file = FileRequest(path, ed2k=ed2k).doRequest()
    if not file:
        return False
    file = file[0]

    # get some necessary attributes
    aid = file.get('aid', None)
    eid = file.get('eid', None)

    # get and index the anime info
    AnimeInfo(aid)
    anime = Anime.get({'id':aid})
    file['name'] = anime.name

    print("found {name} - {epno} {title}".format(**file))

    # rename and move the file
    new_path = rename_file(path, file)

    # should update the row if it does exist?
    if not File.exists({'ed2k':ed2k}):
        # index the file data
        File.add({
            'ed2k': ed2k,
            'path': new_path,
            'aid': aid,
            'eid': eid
        })

def hash_file(file):
    hashable = ['.mkv', '.avi', '.mp4']
    root, ext = splitext(file)

    if not ext.lower() in hashable:
        return

    if not File.exists({'path':file}):
        hash = ed2k.hash(file)
        if not File.exists({'ed2k':hash}):
            index_file(file, hash)

def hash_files(files):
    print("started hash worker")
    for index, file in enumerate(files):
        print("({}/{}) {}".format(index+1, len(files), file))
        hash_file(file)
        print('done')
        print()

def get_files(path):
    to_hash = set()
    for root, dirs, files in walk(path):
        to_hash.update([join(root, f) for f in files])
    return to_hash

def hash_directory(path):
    AuthRequest().doRequest()
    to_hash = sorted(list(get_files(path)))
    to_hash.reverse()
    hash_files(to_hash)
    LogoutRequest().doRequest()

