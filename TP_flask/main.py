import random
import flask
import time
import data_poudlard

app = flask.Flask(__name__)

if __name__ == '__main__':
    app.run()

@app.route("/accueil")
def accueil():
    return flask.render_template("accueil.html")

@app.route("/pagesurdemande")
def page_sur_demande():
    val_random = random.randint(0,100)
    h = time.localtime().tm_hour
    return flask.render_template("pagesurdemande.html", val_random = val_random, h = h)

@app.route("/potions")
def potions():
    return flask.render_template("potions.html", liste_pot = data_poudlard.liste_pot)