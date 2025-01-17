from datetime import timedelta # Pour gérer la durée de la session et la date du jour
import flask # Importation de la bibliothèque flask
from passlib.context import CryptContext # Importation de la bibliothèque passlib pour gérer les mots de passe
import db_pa as db # Importation du module db_yacine.py pour se connecter à la base de données
#import db_liam as db 
password_ctx = CryptContext(schemes=["bcrypt"])

app = flask.Flask(__name__)
app.secret_key = 'super_secret' # Clé secrète pour sécuriser la session
app.permanent_session_lifetime = timedelta(days=30)  # La session expirera après 30 jours
@app.context_processor 
def inject_session():
    return dict(session=flask.session) # Permet d'accéder à la session dans les templates

@app.route("/")
def home():
    return flask.redirect(flask.url_for('boutique')) # En gros permet de rediriger vers la boutique quand aucun chemin est spécifié

@app.route("/boutique", methods=["GET"])
def boutique():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    trie = flask.request.args.get('trie') # Récupère la valeur de l'argument 'trie' dans l'URL
    if trie == 'note':
        cur.execute('SELECT * FROM Boutique ORDER BY boutique.noteMoyenne DESC;')
    elif trie == 'date':
        cur.execute('SELECT * FROM Boutique ORDER BY boutique.date_de_sortie DESC;')
    elif trie == 'nb_ventes':
        cur.execute('SELECT * FROM Boutique ORDER BY boutique.NombreVentes DESC;')
    else:
        cur.execute('SELECT * FROM Boutique ORDER BY titre;')
    jeux = cur.fetchall()
    cur.close()
    conn.close()
    return flask.render_template("boutique.html", jeux = jeux)

@app.route("/profil/<int:joueur_id>")
def profil(joueur_id):
    est_ami = False

    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM Joueur WHERE idJoueur = %s;", (joueur_id,))
    joueur = cur.fetchone()
    if joueur is None: # Si le joueur n'existe pas, on redirige vers la boutique
        return flask.redirect(flask.url_for('boutique'))
    cur.execute("""SELECT J.*
            FROM JoueurJeu JJ
            JOIN Jeu J ON JJ.idJeu = J.idJeu
            WHERE JJ.idJoueur = %s;""", (joueur_id,)) # Permet de récupérer l'ensemble des jeux possédés
    
    possede = cur.fetchall()
    
    cur.execute("""SELECT jeu.*, partage.idJoueur1, partage.idJoueur2
                FROM Jeu
                JOIN Partage ON jeu.idJeu = partage.idJeu
                WHERE partage.idjoueur2 = %s;""", (joueur_id,)) # p.idJoueur2 est le joueur qui reçoit le jeu tandis que p.idJoueur1 est le joueur qui partage le jeu
    partage = cur.fetchall()
    
    cur.execute("""SELECT commentaire.*, jeu.titre AS jeu_titre, jeu.idjeu AS jeu_id, joueur.pseudo
                    FROM Jeu JOIN Commentaire ON jeu.idjeu = commentaire.idjeu JOIN Joueur ON commentaire.idjoueur = joueur.idjoueur 
                    WHERE commentaire.idjoueur = %s;""", (joueur_id,)) # Permet de récupérer l'ensemble des commentaires ainsi que les informations des jeux et des joueurs
    commentaires = cur.fetchall()
    
    cur.execute("SELECT * FROM JoueurAmis WHERE idJoueur1 = %s", (joueur_id,)) # Dans un premier temps on récupère les amis du joueur
    amis = cur.fetchall()
    infos_amis = [] # Dictionnaire pour stocker les informations des amis
    for ami in amis:
        if ami.idjoueur1 == joueur_id: # On vérifie que le joueur est bien le joueur1 de l'amitié car la table JoueurAmis stocke le produit cartésien des amitiés
            cur.execute("SELECT * FROM Joueur WHERE idJoueur = %s;", (ami.idjoueur2,)) # On récupère les informations
            infos_amis.append(cur.fetchone())
    
    cur.execute("SELECT Jeu.idJeu, COUNT(Succes.idSucces) AS total_succes FROM Jeu LEFT JOIN Succes ON Jeu.idJeu = Succes.idJeu GROUP BY Jeu.idJeu;")
    liste_jeux = cur.fetchall()
    
    taux_completion_jeux = {}
    for jeu in liste_jeux:
        cur.execute("SELECT COUNT(*) AS succes_debloques FROM JoueurSucces JOIN Succes ON JoueurSucces.idSucces = Succes.idSucces WHERE JoueurSucces.idJoueur = %s AND Succes.idJeu = %s", (joueur_id, jeu.idjeu))
        succes_debloques = cur.fetchone().succes_debloques
        
        if jeu.total_succes > 0: # On évite la division par zéro
            taux_completion = (succes_debloques / jeu.total_succes) * 100 # Calcul du taux de complétion    
        else:
            taux_completion = 0 # Sinon c'est 0
            
        taux_completion_jeux[jeu.idjeu] = taux_completion
    
    cur.execute("SELECT idSucces FROM JoueurSucces WHERE idJoueur = %s;", (joueur_id,)) # On récupère les succès obtenus par le joueur
    succes_obtenus = cur.fetchall()
    infos_succes = []
    for succes in succes_obtenus:
        cur.execute("SELECT * FROM Succes where idsucces = %s;", (succes.idsucces,)) # On récupère les informations des succès
        infos_succes.append(cur.fetchone())
    print(infos_succes)
    
    
    if "user_id" in flask.session and flask.session["user_id"] != joueur_id: # On vérifie si l'utilisateur est connecté et si le profil consulté n'est pas le sien
        cur.execute("SELECT * FROM JoueurAmis WHERE idJoueur1 = %s AND idJoueur2 = %s;", (flask.session["user_id"], joueur_id)) # On vérifie si les deux joueurs sont amis
        if cur.fetchone(): # Si la requête retourne c'est que les deux joueurs sont amis
            est_ami = True
    
    cur.close()
    conn.close()
    return flask.render_template("profil.html", possede=possede, partage=partage, commentaires=commentaires, joueur=joueur, taux_completion_jeux=taux_completion_jeux, infos_amis=infos_amis, succes_obtenus=infos_succes, est_ami = est_ami)

@app.route("/supprimer_commentaire/<int:id_commentaire>")
def supprimer_commentaire(id_commentaire):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    cur.execute("DELETE FROM Commentaire WHERE idCommentaire = %s;", (id_commentaire,))
    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('profil', joueur_id = flask.session["user_id"]))

@app.route("/reapprovisionnement", methods=["POST"])
def reapprovisionner():
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)

    montant = int(flask.request.form.get("montant"))
    if montant <= 0: # On vérifie que le montant est positif
        return flask.redirect(flask.url_for('profil', joueur_id = flask.session["user_id"]))
    cur.execute("SELECT solde FROM Joueur WHERE idjoueur = %s;", (flask.session["user_id"],))
    solde = cur.fetchone()
    solde = solde[0]
    solde += montant
    cur.execute("UPDATE joueur SET solde = %s WHERE idjoueur = %s", (solde, flask.session["user_id"]))

    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('profil', joueur_id = flask.session["user_id"]))

@app.route("/commentaire/<int:id_jeu>", methods=["POST"])
def commenter(id_jeu):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    commentaire = flask.request.form.get("textecommentaire")
    note = int(flask.request.form.get("note"))
    cur.execute("SELECT * FROM Commentaire WHERE idJeu = %s AND idJoueur = %s;", (id_jeu, flask.session['user_id'])) # On vérifie si le joueur a déjà commenté le jeu
    if cur.fetchone():
        cur.execute("UPDATE Commentaire SET texteCommentaire = %s, note = %s WHERE idJeu = %s AND idJoueur = %s;", (commentaire, note, id_jeu, flask.session['user_id'])) # Si oui, on met à jour le commentaire
    else:
            cur.execute("SELECT MAX(idCommentaire) FROM Commentaire;") # Sinon on récupère l'id maximum pour pourvoir ajouter un nouveau commentaire ensuite
            max_id = cur.fetchone()
            if max_id is None:
                new_id = 1
            else:
                new_id = max_id.max + 1
            cur.execute("INSERT INTO Commentaire (idCommentaire, idJeu, idJoueur, texteCommentaire, note) VALUES (%s, %s, %s, %s, %s);", (new_id ,id_jeu, flask.session['user_id'], commentaire, note)) # Enfin on ajoute
    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('jeu', id=id_jeu))
        
@app.route("/ajout_ami/<int:id_ami>", methods=["POST"])
def ajout_ami(id_ami):
    if 'user_id' in flask.session:
        conn = db.connect()
        cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
        if flask.session['user_id'] < id_ami: # Car dans la base de données on stocke les amitiés dans un sens et pas dans l'autre
            cur.execute("INSERT INTO Amitie (idJoueur1, idJoueur2) VALUES (%s, %s);", (flask.session['user_id'], id_ami))
        else:
            cur.execute("INSERT INTO Amitie (idJoueur1, idJoueur2) VALUES (%s, %s);", (id_ami, flask.session['user_id']))
        cur.close()
        conn.close()
        return flask.redirect(flask.url_for('profil', joueur_id=id_ami))
    else:
        return flask.redirect(flask.url_for('connexion'))
    
@app.route("/supprimer_ami/<int:id_ami>", methods=["POST"])
def supprimer_ami(id_ami):
    if 'user_id' in flask.session:
        conn = db.connect()
        cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
        if flask.session['user_id'] < id_ami:
            cur.execute("DELETE FROM Amitie WHERE idJoueur1 = %s AND idJoueur2 = %s;", (flask.session['user_id'], id_ami))
        else:
            cur.execute("DELETE FROM Amitie WHERE idJoueur1 = %s AND idJoueur2 = %s;", (id_ami, flask.session['user_id']))
        cur.close()
        conn.close()
        return flask.redirect(flask.url_for('profil', joueur_id= id_ami))
    else:
        return flask.redirect(flask.url_for('connexion'))

@app.route("/jeu/<int:id>")
def jeu(id):
    possede = False
    amis = None
    partage = False
    succes_obtenu = None
    achat = False
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    
    cur.execute("SELECT * FROM Boutique WHERE idjeu = %s;", (id,)) 
    jeux = cur.fetchall()
        
    cur.execute("""SELECT commentaire.*, jeu.titre AS jeu_titre, jeu.idjeu AS jeu_id, joueur.pseudo
                    FROM Jeu JOIN Commentaire ON jeu.idjeu = commentaire.idjeu JOIN Joueur ON commentaire.idjoueur = joueur.idjoueur 
                    WHERE commentaire.idjeu = %s;""", (id,)) # Permet de récupérer l'ensemble des commentaires ainsi que les informations des jeux et des joueurs
    commentaires = cur.fetchall()
    
    cur.execute("SELECT * FROM Succes WHERE idJeu= %s;", (id,))
    succes = cur.fetchall()

    if "user_id" in flask.session:
        cur.execute("""SELECT J.*
            FROM JoueurJeu JJ
            JOIN Jeu J ON JJ.idJeu = J.idJeu
            WHERE JJ.idJoueur = %s;""", (flask.session["user_id"],)) # Permet de récupérer l'ensemble des jeux possédés pa le joueur
        jeuxpossede = cur.fetchall()
        for jeu in jeuxpossede:
            if jeu.idjeu == id:
                possede = True # Le joueur a donc le jeu
                
        cur.execute("SELECT * FROM JoueurAmis WHERE idJoueur1 = %s", (flask.session["user_id"],))
        amis = cur.fetchall()

        cur.execute("SELECT * FROM JoueurSucces WHERE idJoueur = %s;", (flask.session["user_id"],))
        succes_obtenu = cur.fetchall()
        print(succes_obtenu)

        cur.execute("SELECT * FROM Partage where idJoueur1 = %s and idJeu = %s", (flask.session["user_id"], id)) # On regarde si le joueur partage le jeu en question
        partage_liste = cur.fetchone()
        if(partage_liste): # Si la requête retourne c'est que le joueur partage le jeu
            partage = True


        cur.execute("SELECT solde FROM Joueur WHERE idjoueur = %s;", (flask.session["user_id"],))
        solde = cur.fetchone()
        solde = solde[0]
        cur.execute("SELECT titre, prix, pegi from jeu WHERE idjeu = %s;", (id,))
        infojeu = cur.fetchone()
        cur.execute("SELECT DATE_PART('year', AGE(date_naissance)) FROM joueur WHERE idjoueur = %s;", (flask.session["user_id"],)) # La fonction DATE_PART() permet d'extraire seulement l'année tandis que la fonction AGE() permet de calculer l'âge à partir de la date de naissance
        age = int(cur.fetchone()[0])
        if age >= infojeu.pegi and solde >= infojeu.prix: # On vérifie si le joueur a l'âge requis et si il a assez d'argent finalement 
            achat = True

    cur.close()
    conn.close()
    return flask.render_template("jeu.html", jeux=jeux, commentaires=commentaires, possede = possede, amis = amis, succes = succes, succes_obtenu = succes_obtenu, partage = partage, achat = achat)


@app.route("/achat_jeu/<int:idjeu>")
def achat_jeu(idjeu):
    if "user_id" in flask.session:
        conn = db.connect()
        cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
        cur.execute("SELECT solde FROM Joueur WHERE idjoueur = %s;", (flask.session["user_id"],))
        solde = cur.fetchone()
        solde = solde[0]
        cur.execute("SELECT titre, prix from jeu WHERE idjeu = %s;", (idjeu,))
        infojeu = cur.fetchone()
        solde -= infojeu.prix
        cur.execute("UPDATE joueur SET solde = %s WHERE idjoueur = %s", (solde, flask.session["user_id"])) 
        cur.execute("INSERT INTO JoueurJeu VALUES (%s, %s)", (flask.session["user_id"], idjeu))
        info = f"Achat du jeu {infojeu.titre}" # Permet d'ajouter l'objet de la transaction dans la table Transaction
        cur.execute("SELECT MAX(idTransaction) FROM Transaction_user;")
        max_id = cur.fetchone() # On récupère l'id maximum pour ajouter une nouvelle transaction
        if max_id is None:
            max_id = 0
        else:
            new_id = max_id.max + 1
        cur.execute("INSERT INTO Transaction_user (idTransaction, idJoueur, idJeu, montant, objet_transaction) VALUES (%s, %s, %s, %s, %s);", (new_id, flask.session["user_id"], idjeu, infojeu.prix, info,))
    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('profil', joueur_id=flask.session["user_id"]))
    
@app.route("/annuler_partage/<int:id_jeu>", methods = ["POST"])
def annuler_partage(id_jeu):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    cur.execute("DELETE FROM Partage where idJoueur1 = %s and idJeu = %s", (flask.session["user_id"], id_jeu))
    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('jeu', id=id_jeu))

@app.route("/partage_jeu/<int:idjeu>", methods = ["POST"])
def partage_jeu(idjeu):
    conn = db.connect()
    cur = conn.cursor(cursor_factory=db.psycopg2.extras.NamedTupleCursor)
    idjoueur = flask.request.form.get('ami')
    print(idjoueur)
    cur.execute("INSERT INTO PARTAGE VALUES (%s, %s, %s);", (flask.session["user_id"], idjoueur, idjeu))
    cur.close()
    conn.close()
    return flask.redirect(flask.url_for('jeu', id=idjeu))

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
        if '@' in user: # On vérifie si monsieur a rentré un email ou un pseudo
            cur.execute("SELECT idJoueur, mot_de_passe FROM Joueur WHERE email = %s;", (user,))
        else:
            cur.execute("SELECT idJoueur, mot_de_passe FROM Joueur WHERE pseudo = %s;", (user,))
        result = cur.fetchone()

        if result:
            etat = 2
            user_id = result.idjoueur
            user_hash = result.mot_de_passe
            verif_mdp = password_ctx.verify(password, user_hash) # On compare les hashs pour vérifier si le mot de passe est correct
            if verif_mdp: # Si c'est le cas on connecte
                etat = 3
                flask.session.permanent = True # La session est permanente
                flask.session['user_id'] = user_id # On stocke l'id du joueur dans la session
                
    cur.close()
    conn.close()
    if(etat != 3): # Si la connexion a échoué
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
        if '@' in email and  '.' in email: # On vérifie si l'email est valide
            cur.execute("SELECT idJoueur FROM Joueur WHERE email = %s;", (email,))
            if(cur.fetchone()):
                etat = 1
                return flask.render_template("inscription.html", etat = etat)
            
            cur.execute("SELECT idJoueur FROM Joueur WHERE pseudo = %s;", (user,))
            if(cur.fetchone() or len(user) < 3 or len(user) > 16): # On vérifie si le pseudo est valide et s'il n'est pas déjà utilisé
                etat = 2
                return flask.render_template("inscription.html", etat = etat)
            
            if(len(password) < 8): # On vérifie si le mot de passe est assez long minimum de sécurité ici
                etat = 3
                return flask.render_template("inscription.html", etat = etat)
            
            if etat == 0: # Tout est bon on peut insérer le joueur dans la base lesssgo
                cur.execute("SELECT MAX(idJoueur) FROM Joueur;")
                max_id = cur.fetchone()
                if max_id is None:
                    new_id = 1
                else:
                    new_id = max_id.max + 1
                
                hash_pw = password_ctx.hash(password) # Calcul du hash du mot de passe à stocker
                cur.execute("INSERT INTO Joueur (idJoueur, pseudo, email, mot_de_passe, nom, date_naissance, solde) VALUES (%s ,%s, %s, %s, %s, %s, 0);", (new_id ,user, email, hash_pw, nom, datenaissance))
            cur.close()
            conn.close()
            
        if etat == 0:
            return flask.redirect(flask.url_for('connexion'))
        
    return flask.render_template("inscription.html", etat = etat)

if __name__ == '__main__':
    app.run(debug=True)

