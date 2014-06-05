from flask import Flask, render_template, send_file, request, redirect, flash
import os.path

from config import image_store
from animeinfo import Anime
from search import search

import index
from nyaa import Nyaa

app = Flask(__name__)
app.secret_key = 'nice boat'

@app.route('/images/<path:filename>')
def images(filename):
  name = os.path.basename(filename)
  path = image_store.strip() + name.strip()
  return send_file(path)

@app.route('/search')
def find_anime():
    term = request.args.get('term')
    results = search(term)
    return render_template('search.html', results=results)

@app.route('/download/<eid>')
def download_episode(eid):
    episode = index.get_episode(eid)
    name = str(episode.anime)
    epno = episode.epno

    nyaa = Nyaa()
    torrent = nyaa.find_torrent(name, epno=epno)
    if torrent:
        title, link = torrent
        nyaa.download_torrent(link, title)
        flash('Downloaded torrent for {0}'.format(title))
    else:
        flash('Failed to find torrent for {0} episode {1}'.format(name, epno))

    return redirect('/anime/' + str(episode.anime.id))

@app.route('/anime/<aid>')
def anime(aid):
  anime = Anime(aid)
  if anime.xml == None:
    return "That AID isn't right"
  indexed_anime = index.get_anime(aid)
  episodes = indexed_anime.episodes if indexed_anime is not None else []
  return render_template("anime.html", anime=indexed_anime, episodes=episodes)

@app.route('/')
def indexed_anime():
  print("HI")
  anime = index.get_all_anime()
  return render_template("index/anime.html", anime=anime)

if __name__ == "__main__":
  app.run(debug=True)

