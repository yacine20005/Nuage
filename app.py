import time
import flask
import db_yacine as db # Importation du module db_yacine.py
#import db_liam as db
from passlib.context import CryptContext
password_ctx = CryptContext(schemes=["bcrypt"]) # Création d'un objet pour gérer les mots de passe
session = {} # Dictionnaire pour stocker les informations de session

app = flask.Flask(__name__)

@app.context_processor
def inject_session():
    return dict(session=session) # Permet d'accéder à la session dans les templates

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
    return flask.render_template("boutique.html", jeux = jeux)

@app.route('/recherche', methods=['GET'])
def recherche():
    resultats = []
    query = flask.request.args.get('recherche')
    if(query):
        type_recherche = flask.request.args.get('type-recherche')
        if(type_recherche in ["titre", "genres", "developpeur", "editeur"]):
            conn = db.connect()
            cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
            cur.execute(f"SELECT * FROM Boutique WHERE {type_recherche} ILIKE %s", ('%' + query + '%',)) # Utilisation de ilike pour ignorer la casse des caractères
            resultats = cur.fetchall()
            cur.close()
            conn.close()
            print(resultats)
    return flask.render_template("recherche.html", resultats=resultats)



@app.route("/profil")
def profil():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM profil WHERE idJoueur = %s;", (session["user_id"],))
    resultats = cur.fetchall()
    
    cur.execute("SELECT pseudo FROM profil WHERE idJoueur = %s;", (session["user_id"],))
    pseudo = cur.fetchall()
    pseudo = pseudo[0].pseudo # Permet de récupérer le pseudo de l'utilisateur sans le tuple
    
    cur.execute("SELECT * FROM commentairejeu WHERE Joueur = %s;", (session["user_id"],))
    commentaires = cur.fetchall()
    conn.close()
    return flask.render_template("profil.html", resultats = resultats, pseudo = pseudo, commentaires = commentaires)


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    etat = 0 # 0 si rien, 1 si pseudo/mail faux, 2 si mdp faux, 3 si connexion reussie!
    user = flask.request.form.get('user')
    password = flask.request.form.get('password')
    
    if user and password :
        etat = 1
        if '@' in user:
            cur.execute("SELECT idJoueur, mot_de_passe FROM Joueur WHERE email = %s;", (user,))
        else:
            cur.execute("SELECT idJoueur, mot_de_passe FROM Joueur WHERE pseudo = %s;", (user,))
        result = cur.fetchone()

        if result:
            etat = 2
            user_id = result.idjoueur
            user_hash = result.mot_de_passe
            verif_mdp = password_ctx.verify(password, user_hash)
            if verif_mdp:
                etat = 3
                session['user_id'] = user_id
                
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
                cur.execute("SELECT MAX(idJoueur) FROM Joueur;")
                max_id = cur.fetchone()
                if max_id is None:
                    max_id = 0
                else:
                    new_id = max_id.max + 1
                
                hash_pw = password_ctx.hash(password) #Calcul du hash du mot de passe à stocker
                cur.execute("INSERT INTO Joueur (idJoueur, pseudo, email, mot_de_passe, nom, date_naissance, solde) VALUES (%s ,%s, %s, %s, %s, %s, 0);", (new_id ,user, email, hash_pw, nom, datenaissance))
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
