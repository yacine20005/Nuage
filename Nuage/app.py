import random
import time
import flask

app = flask.Flask(__name__)

if __name__ == '__main__':
    app.run()

@app.route("/boutique")
def boutique():
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    s = time.localtime().tm_sec
    return flask.render_template("boutique.html", h = h, m = m, s = s)

@app.route("/recherche")
def recherche():
    return flask.render_template("recherche.html")