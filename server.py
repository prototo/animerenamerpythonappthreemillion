from flask import Flask, render_template, send_file
import os.path

from config import image_store
from animeinfo import Anime

app = Flask(__name__)

@app.route('/images/<path:filename>')
def images(filename):
  name = os.path.basename(filename)
  path = image_store.strip() + name.strip()
  return send_file(path)

@app.route('/anime/<aid>')
def anime(aid):
  anime = Anime(aid)
  if anime == None:
    return "That AID isn't right"
  return render_template("anime.html", anime=anime)

if __name__ == "__main__":
  app.run(debug=True)

