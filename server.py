from flask import Flask, render_template

from animeinfo import Anime

app = Flask(__name__)

@app.route('/anime/<aid>')
def anime(aid):
  anime = Anime(aid)
  if anime == None:
    return "That AID isn't right"
  return render_template("anime.html", anime=anime)

if __name__ == "__main__":
  app.run(debug=True)

