from flask import Flask, render_template, send_file, request, redirect, flash
import os.path

from config import image_store
from animeinfo import Anime
from search import search

import index
from nyaa import Nyaa

from tvdb import TVDB
tvdb = TVDB()

app = Flask(__name__)
app.secret_key = 'nice boat'

@app.route('/images/<path:filename>')
def images(filename):
    try:
        name = os.path.basename(filename)
        path = os.path.join(image_store.strip(), name.strip())
        return send_file(path)
    except:
        return ''

@app.route('/search')
def find_anime():
    term = request.args.get('term')
    results = search(term)
    return render_template('search.html', results=results)

@app.route('/download/episode/<eid>')
def download_episode(eid):
    episode = index.get_episode(eid)
    anime = index.get_anime(episode.aid)

    nyaa = Nyaa([
        anime.name, anime.name_ro, anime.name_jp
    ])
    #(link, title)
    torrent = nyaa.find_episode(episode.epno)

    if torrent[0]:
        link, title = torrent
        nyaa.download_torrent(link, title)
        flash('Downloaded torrent {0}'.format(title))
    else:
        flash('Failed to find torrent for {0} episode {1}'.format(anime.name, episode.epno))

    return redirect('/anime/' + str(episode.anime.id))

@app.route('/download/anime/<aid>')
def download_anime(aid):
    anime = index.get_anime(aid)
    episodes = anime.episodes
    nyaa = Nyaa([
        anime.name, anime.name_ro, anime.name_jp
    ])
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

