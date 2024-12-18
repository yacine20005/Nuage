from datetime import timedelta # Pour gérer la durée de la session et la date du jour
import flask
from passlib.context import CryptContext
#import db_yacine as db
import db_liam as db
password_ctx = CryptContext(schemes=["bcrypt"]) # Création d'un objet pour gérer les mots de passe

app = flask.Flask(__name__)
app.secret_key = 'super_secret'
app.permanent_session_lifetime = timedelta(days=30)  # La session expirera après 30 jours
@app.context_processor
def inject_session():
    return dict(session=flask.session) # Permet d'accéder à la session dans les templates

@app.route("/")
def home():
    return flask.redirect(flask.url_for('boutique'))

@app.route("/boutique")
def boutique():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    cur.execute('SELECT * FROM Boutique;')
    jeux = cur.fetchall()
    cur.close()
    conn.close()
    return flask.render_template("boutique.html", jeux = jeux)

@app.route("/profil/<int:joueur_id>")
def profil(joueur_id):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM Joueur WHERE idJoueur = %s;", (joueur_id,))
    joueur = cur.fetchone()
    
    cur.execute("""SELECT J.*
            FROM JoueurJeu JJ
            JOIN Jeu J ON JJ.idJeu = J.idJeu
            WHERE JJ.idJoueur = %s;""", (joueur_id,))
    
    possede = cur.fetchall()
    
    cur.execute("""SELECT jeu.*, partage.idJoueur1, partage.idJoueur2
                FROM Jeu
                JOIN Partage ON jeu.idJeu = partage.idJeu
                WHERE partage.idjoueur2 = %s;""", (joueur_id,)) # p.idJoueur2 est le joueur qui reçoit le jeu tandis que p.idJoueur1 est le joueur qui partage le jeu
    partage = cur.fetchall()
    
    cur.execute("""SELECT commentaire.*, jeu.titre AS jeu_titre, jeu.idjeu AS jeu_id, joueur.pseudo
                    FROM Jeu JOIN Commentaire ON jeu.idjeu = commentaire.idjeu JOIN Joueur ON commentaire.idjoueur = joueur.idjoueur 
                    WHERE commentaire.idjoueur = %s;""", (joueur_id,))
    commentaires = cur.fetchall()
    
    cur.execute("SELECT * FROM JoueurAmis WHERE idJoueur1 = %s", (joueur_id,))
    amis = cur.fetchall()
    infos_amis = [] # Dictionnaire pour stocker les informations des amis
    for ami in amis:
        if ami.idjoueur1 == flask.session["user_id"]:
            cur.execute("SELECT * FROM Joueur WHERE idJoueur = %s;", (ami.idjoueur2,))
            infos_amis.append(cur.fetchone())
    
    cur.execute("SELECT Jeu.idJeu, COUNT(Succes.idSucces) AS total_succes FROM Jeu LEFT JOIN Succes ON Jeu.idJeu = Succes.idJeu GROUP BY Jeu.idJeu;")
    liste_jeux = cur.fetchall()
    
    taux_completion_jeux = {}
    for jeu in liste_jeux:
        cur.execute("SELECT COUNT(*) AS succes_debloques FROM JoueurSucces JOIN Succes ON JoueurSucces.idSucces = Succes.idSucces WHERE JoueurSucces.idJoueur = %s AND Succes.idJeu = %s", (joueur_id, jeu.idjeu))
        succes_debloques = cur.fetchone().succes_debloques
        
        if jeu.total_succes > 0:
            taux_completion = (succes_debloques / jeu.total_succes) * 100
        else:
            taux_completion = 0
            
        taux_completion_jeux[jeu.idjeu] = taux_completion
    
    cur.close()
    conn.close()
    return flask.render_template("profil.html", possede=possede, partage=partage, commentaires=commentaires, joueur=joueur, taux_completion_jeux=taux_completion_jeux, infos_amis=infos_amis)

@app.route("/reapprovisionnement", methods=["POST"])
def reapprovisionner():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)

    montant = int(flask.request.form.get("montant"))
    if montant <= 0:
        return flask.redirect(flask.url_for('profil', joueur_id = flask.session["user_id"]))
    cur.execute("SELECT solde FROM Joueur WHERE idjoueur = %s;", (flask.session["user_id"],))  # Utilisation de paramètres préparés pour éviter l'injection SQL car psycopg2 se charge de gérer la valeur
    solde = cur.fetchone()
    solde = solde[0]
    solde += montant
    cur.execute("UPDATE joueur SET solde = %s WHERE idjoueur = %s", (solde, flask.session["user_id"]))

    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('profil', joueur_id = flask.session["user_id"]))

@app.route("/ajout_ami/<int:id_ami>", methods=["POST"])
def ajout_ami(id_ami):
    if 'user_id' in flask.session:
        conn = db.connect()
        cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
        if flask.session['user_id'] < id_ami:
            cur.execute("INSERT INTO Amitie (idJoueur1, idJoueur2) VALUES (%s, %s);", (flask.session['user_id'], id_ami))
        else:
            cur.execute("INSERT INTO Amitie (idJoueur1, idJoueur2) VALUES (%s, %s);", (id_ami, flask.session['user_id']))
        cur.close()
        conn.close()
        return flask.redirect(flask.url_for('profil', joueur_id=id_ami))
    else:
        return flask.redirect(flask.url_for('connexion'))

@app.route("/jeu/<int:id>")
def jeu(id):
    possede = False
    amis = None
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM Boutique WHERE idjeu = %s;", (id,))  # Utilisation de paramètres préparés pour éviter l'injection SQL car psycopg2 se charge de gérer la valeur
    jeux = cur.fetchall()
        
    cur.execute("""SELECT commentaire.*, jeu.titre AS jeu_titre, jeu.idjeu AS jeu_id, joueur.pseudo
                    FROM Jeu JOIN Commentaire ON jeu.idjeu = commentaire.idjeu JOIN Joueur ON commentaire.idjoueur = joueur.idjoueur 
                    WHERE commentaire.idjeu = %s;""", (id,))
    commentaires = cur.fetchall()
    
    if "user_id" in flask.session:
        cur.execute("""SELECT J.*
            FROM JoueurJeu JJ
            JOIN Jeu J ON JJ.idJeu = J.idJeu
            WHERE JJ.idJoueur = %s;""", (flask.session["user_id"],))
        jeuxpossede = cur.fetchall()
        for jeu in jeuxpossede:
            if jeu.idjeu == id:
                possede = True
        cur.execute("SELECT * FROM JoueurAmis WHERE idJoueur1 = %s", (flask.session["user_id"],))
        amis = cur.fetchall()
        print(amis)

    cur.close()
    conn.close()
    return flask.render_template("jeu.html", jeux=jeux, commentaires=commentaires, possede = possede, amis = amis)


@app.route("/achat_jeu/<int:idjeu>")
def achat_jeu(idjeu):
    if "user_id" in flask.session:
        conn = db.connect()
        cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)

        cur.execute("SELECT solde FROM Joueur WHERE idjoueur = %s;", (flask.session["user_id"],))  # Utilisation de paramètres préparés pour éviter l'injection SQL car psycopg2 se charge de gérer la valeur
        solde = cur.fetchone()
        solde = solde[0]
        cur.execute("SELECT titre, prix from jeu WHERE idjeu = %s;", (idjeu,))
        infojeu = cur.fetchone()
        if solde < infojeu.prix:
            return "Solde insufissant a l'achat"
        else:
            solde -= infojeu.prix
            cur.execute("UPDATE joueur SET solde = %s WHERE idjoueur = %s", (solde, flask.session["user_id"]))
            cur.execute("INSERT INTO JoueurJeu VALUES (%s, %s)", (flask.session["user_id"], idjeu))
            info = f"Achat du jeu {infojeu.titre}"
            print(info)
            cur.execute("SELECT MAX(idTransaction) FROM Transaction_user;")
            max_id = cur.fetchone()
            if max_id is None:
                max_id = 0
            else:
                new_id = max_id.max + 1
            cur.execute("INSERT INTO Transaction_user (idTransaction, idJoueur, idJeu, montant, objet_transaction) VALUES (%s, %s, %s, %s, %s);", (new_id, flask.session["user_id"], idjeu, infojeu.prix, info,))
    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('profil', joueur_id=flask.session["user_id"]))
    

@app.route("/partage_jeu/<int:idjeu>", methods = ["Post"])
def partage_jeu(idjeu):
    """CREATE TABLE Partage (
    idJoueur1 INT,
    idJoueur2 INT,
    idJeu INT,"""
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    idjoueur = flask.request.form.get('ami')
    cur.execute("INSERT INTO PARTAGE VALUES (%s, %s, %s);", (flask.session["user_id"], idjoueur, idjeu))
    cur.close()
    conn.close()



@app.route("/deconnexion")
def deconnexion():
    flask.session.clear()  # Supprime 'user_id' de la session
    return flask.redirect(flask.url_for('boutique'))  # Redirige vers la boutique

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
    return flask.render_template("recherche.html", resultats=resultats)

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
                flask.session.permanent = True
                flask.session['user_id'] = user_id
                
    cur.close()
    conn.close()
    if(etat != 3):
        return flask.render_template("connexion.html", etat = etat)
    else:
        return flask.redirect(flask.url_for('boutique'))

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

if __name__ == '__main__':
    app.run(debug=True)
