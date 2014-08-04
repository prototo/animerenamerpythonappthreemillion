from flask import Flask, render_template, send_file, request, redirect, flash
import os.path
from config import image_store
from lib.anidb.animeinfo import Anime
from arpatm.search import search
import lib.index as index
from lib.tvdb import TVDB
from lib.nyaa import Nyaa

tvdb = TVDB()

app = Flask(__name__)
app.secret_key = 'nice boat'

@app.route('/images/<path:filename>')
def images(filename):
    try:
        name = os.path.basename(filename)
        path = os.path.join(image_store.strip(), name.strip())
        path = os.path.abspath(path)
        return send_file(path)
    except:
        return ''

@app.route('/search')
def find_anime():
    term = request.args.get('term')
    results = search(term)
    return render_template('search.html', results=results, term=term)

@app.route('/torrents/episode/<eid>')
def episode_torrents(eid):
    episode = index.get_episode(eid)
    nyaa = Nyaa(episode.aid)
    torrents = nyaa.find_episode(episode.epno)

    from urllib.parse import quote
    links = ['<a href="/download/episode/{}">{}</a>'.format(quote(link), title) for (link, title) in torrents]

    return '</br>'.join(links)

@app.route('/download/episode/<path:path>')
def download_episode(path):
    Nyaa.download_torrent(path)
    return redirect(request.referrer)

@app.route('/download/anime/<aid>')
def download_anime(aid):
    anime = index.get_anime(aid)
    episodes = anime.episodes
    nyaa = Nyaa(aid)
    torrents = nyaa.find_episodes(episodes)
    nyaa.download_torrents(torrents)

    for torrent in torrents:
        flash('Downloaded torrent {0}'.format(torrent[1]))

    return redirect('/anime/' + aid)

@app.route('/anime/<aid>')
def anime(aid):
    anime = Anime(aid)
    if anime.xml == None:
        return "That AID isn't right"
    indexed_anime = index.get_anime(aid)
    episodes = indexed_anime.episodes if indexed_anime is not None else []

    # get images from tvdb
    splash = poster = None
    for title in indexed_anime.get_names():
        if not splash:
            splash = tvdb.get_fanart(title)
        if not poster:
            poster = tvdb.get_poster(title)

    return render_template("anime.html", anime=indexed_anime, episodes=episodes, splash=splash, poster=poster)

@app.route('/')
def indexed_anime():
    anime = index.get_all_anime()
    return render_template("index/anime.html", anime=anime)

def run():
    app.run(debug=True, host='0.0.0.0')

if __name__ == "__main__":
    run()
