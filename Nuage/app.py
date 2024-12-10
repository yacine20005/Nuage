import time
import flask
import db
from psycopg2 import sql

app = flask.Flask(__name__)

@app.route("/boutique")
def boutique():
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    s = time.localtime().tm_sec
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    cur.execute('SELECT * FROM Boutique;')
    jeux = cur.fetchall()
    cur.close()
    conn.close()
    return flask.render_template("boutique.html", h = h, m = m, s = s, jeux = jeux)

@app.route('/recherche', methods=['GET'])
def recherche():
    resultats = []
    query = flask.request.args.get('recherche')
    if(query):
        query = query.lower()
        type_recherche = flask.request.args.get('type-recherche')
        if(type_recherche in ["titre", "genres", "developeur", "editeur"]):
            conn = db.connect()
            cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
             
            cur.execute(f"SELECT * FROM Boutique WHERE {type_recherche} ILIKE %s", ('%' + query + '%',))

            resultats = cur.fetchall()
            cur.close()
            conn.close()
            print(resultats)
    return flask.render_template("recherche.html", resultats=resultats)



@app.route("/profil")
def profil():
    return flask.render_template("profil.html")

@app.route("/connexion")
def connexion():
    return flask.render_template("connexion.html")

@app.route("/inscription")
def inscription():
    return flask.render_template("inscription.html")

@app.route("/jeu/<int:id>")
def jeu(id):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM Boutique WHERE idjeu = %s;", (id,))  # Utilisation de paramètres préparés pour éviter l'injection SQL car psycopg2 se charge de gérer la valeur
    jeux = cur.fetchall()
        
    cur.execute("SELECT * FROM CommentaireJeu WHERE idjeu = %s;", (id,))
    commentaires = cur.fetchall()
    
    cur.close()
    conn.close()
    return flask.render_template("jeu.html", jeux=jeux, commentaires=commentaires)

if __name__ == '__main__':
    app.run(debug=True)
