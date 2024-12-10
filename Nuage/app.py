import time
import flask
import db
from passlib.context import CryptContext
password_ctx = CryptContext(schemes=["bcrypt"])
session = {}

app = flask.Flask(__name__)
app.secret_key = 'WeekendAvecPrisci'  # Remplace par une vraie clé secrète

@app.context_processor
def inject_session():
    return dict(session=session)

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

@app.route("/connexion2", methods=["GET", "POST"])
def connexion2():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    etat = 1 #0 si rien, 1 si pseudo/mail faux, 2 si mdp faux !
    user = flask.request.form.get('user')
    password = flask.request.form.get('password')
    if user and password : 
        if '@' in user:
            cur.execute("SELECT idJoueur FROM Joueur WHERE emial = %s;", (user,))
        else:
            cur.execute("SELECT idJoueur FROM Joueur WHERE pseudo = %s;", (user,)) 
        user_id = cur.fetchone()
        user_id = user_id[0] if user_id else None
        if(user_id):
            etat = 2
            #tu prend son mdp et tu le compare avec le hash de celui qu'il as mis
            cur.execute("SELECT mot_de_passe FROM Joueur WHERE idjoueur = %s;", (user_id,))
            user_hash = cur.fetchone()
            user_hash = user_hash[0] if user_hash else None
            if user_hash and password_ctx.verify(password, user_hash):  #et si tout est bon il est connecté
                session['user_id'] = user_id
                etat = 0
    cur.close()
    conn.close()
    return flask.render_template("connexion.html", etat = etat)


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    etat = 1 #0 si rien, 1 si pseudo/mail faux, 2 si mdp faux !
    user = flask.request.form.get('user')
    password = flask.request.form.get('password')
    if user and password : 
        if '@' in user:
            cur.execute("SELECT idJoueur FROM Joueur WHERE emial = %s;", (user,))
        else:
            cur.execute("SELECT idJoueur FROM Joueur WHERE pseudo = %s;", (user,)) 
        user_id = cur.fetchone()
        user_id = user_id[0] if user_id else None
        #Utilisateur trouvé
        if(user_id):
            etat = 2
            #tu prend son mdp et tu le compare avec le hash de celui qu'il as mis
            cur.execute("SELECT mot_de_passe FROM Joueur WHERE idjoueur = %s;", (user_id,))
            user_hash = cur.fetchone()
            user_hash = user_hash[0] if user_hash else None
            if user_hash == password:  #et si tout est bon il est connecté
            #if user_hash and password_ctx.verify(password, user_hash):  #verification a rajoute pour prendre en compte les hash
                session['user_id'] = user_id
                etat = 0
    print(etat)
    cur.close()
    conn.close()
    if(etat):
        return flask.render_template("connexion.html", etat = etat)
    else:
        return flask.redirect(flask.url_for('boutique'))
        

@app.route("/deconnexion")
def deconnexion():
    if 'user_id' in session:  # Vérifie si 'user_id' est présent dans la session
        session.pop('user_id')  # Supprime 'user_id' de la session
    return flask.redirect(flask.url_for('boutique'))  # Redirige vers la boutique


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
