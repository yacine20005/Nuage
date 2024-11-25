import random
import os
from werkzeug.utils import secure_filename # Permet de sécuriser le nom du fichier
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
    cur = conn.cursor()
    cur.execute('SELECT * FROM Boutique;')
    jeux = cur.fetchall()
    print(jeux)
    cur.close()
    conn.close()
    return flask.render_template("boutique.html", h = h, m = m, s = s, jeux = jeux)

@app.route("/recherche")
def recherche():
    return flask.render_template("recherche.html")

@app.route('/upload', methods=['POST']) # Route pour l'upload de fichier
def upload_file():
    if 'file' not in flask.request.files: # Vérifier si un fichier a été envoyé
        return 'No file part'
    file = flask.request.files['file'] # Récupérer le fichier
    if file.filename == '': # Vérifier si le fichier a un nom
        return 'No selected file'
    if file: # Si le fichier est correct
        filename = secure_filename(file.filename) # Sécuriser le nom du fichier
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # Enregistrer le fichier
        return flask.redirect(flask.url_for('uploaded_file', filename=filename))
    
if __name__ == '__main__':
    app.run(debug=True)