from http.client import HTTPConnection
from urllib.parse import urlencode
from json import dumps, loads

host = 'localhost'
host = 'onodera'
port = 9091
path = '/transmission/rpc'
session_id = None

def resolve(link):
    from urllib.parse import urlsplit
    result = urlsplit(link)

    con = HTTPConnection(result.netloc)
    con.request('GET', result.path + '?' + result.query)
    res = con.getresponse()

    location = res.getheader('Location')
    if location:
        return location
    return False

def add(link):
    global session_id
    method = 'torrent-add'
    data = {
        'method': method,
        'arguments': {
            'filename': link
        }
    }

    con = HTTPConnection(host, port)
    headers = {}
    if session_id:
        headers['X-Transmission-Session-Id'] = session_id

    con.request('POST', path, body=dumps(data), headers=headers)
    res = con.getresponse()

    if res.status == 409:
        session_id = res.getheader('X-Transmission-Session-Id')
        return add(link)

    body = loads(res.read().decode())
    if not 'result' in body or body['result'] != 'success':
        link = resolve(link)
        if link:
            add(link)
    else:
        # success!
        pass