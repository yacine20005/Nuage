import time
import flask
import db

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads' # Dossier de stockage des fichiers

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

@app.route("/recherche")
def recherche():
    return flask.render_template("recherche.html")

@app.route("/jeu/<int:id>")
def jeu(id):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM Boutique WHERE idjeu = %s;", (id,))  # Utilisation de paramètres préparés pour éviter l'injection SQL car psycopg2 se charge de gérer la valeur
    jeux = cur.fetchall()
    
    cur.execute("SELECT * FROM Commentaire WHERE idjeu = %s;", (id,))
    commentaires = cur.fetchall()
    
    cur.close()
    conn.close()
    return flask.render_template("jeu.html", jeux=jeux, commentaires=commentaires)

if __name__ == '__main__':
    app.run(debug=True)
