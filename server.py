from flask import Flask, render_template, send_file
import os.path

from config import image_store
from animeinfo import Anime

import index

app = Flask(__name__)

@app.route('/images/<path:filename>')
def images(filename):
  name = os.path.basename(filename)
  path = image_store.strip() + name.strip()
  return send_file(path)

@app.route('/anime/<aid>')
def anime(aid):
  anime = Anime(aid)
  if anime.xml == None:
    return "That AID isn't right"
  files = index.get_anime(aid).files
  return render_template("anime.html", anime=anime, files=files)

@app.route('/index/anime')
def indexed_anime():
  print("HI")
  anime = index.get_all_anime()
  return render_template("index/anime.html", anime=anime)

if __name__ == "__main__":
  app.run(debug=True)

