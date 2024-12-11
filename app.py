import time
import flask
import db_yacine as db
from passlib.context import CryptContext
password_ctx = CryptContext(schemes=["bcrypt"])
session = {}

app = flask.Flask(__name__)

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
        type_recherche = flask.request.args.get('type-recherche')
        if(type_recherche in ["titre", "genres", "developpeur", "editeur"]):
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


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    etat = 0 #0 si rien, 1 si pseudo/mail faux, 2 si mdp faux, 3 si connexion reussie!
    user = flask.request.form.get('user')
    password = flask.request.form.get('password')
    if user and password : 
        etat = 1
        if '@' in user:
            cur.execute("SELECT idJoueur FROM Joueur WHERE email = %s;", (user,))
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
                etat = 3
    cur.close()
    conn.close()
    if(etat != 3):
        return flask.render_template("connexion.html", etat = etat)
    else:
        return flask.redirect(flask.url_for('boutique'))
        

@app.route("/deconnexion")
def deconnexion():
    if 'user_id' in session:  # Vérifie si 'user_id' est présent dans la session
        session.pop('user_id')  # Supprime 'user_id' de la session
    return flask.redirect(flask.url_for('boutique'))  # Redirige vers la boutique


@app.route("/inscription", methods=["GET", "POST"])
def inscription():

    etat = 0  # 0 = pas d'erreur, 1 = email déjà utilisé, 2 = pseudo déjà utilisé ou trop long, 3 = mot de passe trop court
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    nom = flask.request.form.get('nom')
    email = flask.request.form.get('email')
    user = flask.request.form.get('user')
    password = flask.request.form.get('password')
    datenaissance = flask.request.form.get('date_de_naissance')
    if(nom and email and user and password and datenaissance):
        if '@' in email and  '.' in email:
            cur.execute("SELECT idJoueur FROM Joueur WHERE email = %s;", (email,))
            if(cur.fetchone()):
                etat = 1
                return flask.render_template("inscription.html", etat = etat) 
            cur.execute("SELECT idJoueur FROM Joueur WHERE pseudo = %s;", (user,))
            if(cur.fetchone() or len(user) < 3 or len(user) > 16):
                etat = 2
                return flask.render_template("inscription.html", etat = etat) 
            if(len(password) < 8):
                etat = 3
                return flask.render_template("inscription.html", etat = etat) 
            if etat == 0:
                hash_pw = password_ctx.hash(password) #Calcul du hash du mot de passe à stocker
                cur.execute("INSERT INTO Joueur (pseudo, email, mot_de_passe, nom, date_naissance, solde) VALUES (%s, %s, %s, %s, %s, 0);", (user, email, hash_pw, nom, datenaissance))
            cur.close()
            conn.close()
        if etat == 0:
            return flask.redirect(flask.url_for('connexion')) 
    return flask.render_template("inscription.html", etat = etat) 

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
