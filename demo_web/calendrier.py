import time
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# Clef secrète utilisée pour chiffrer les cookies
app.secret_key = b'd2b01c987b6f7f0d5896aae06c4f318c9772d6651abff24aec19297cdf5eb199'


### Premier exemple de template

@app.route("/horloge")
def time_string():
  local_time = time.localtime()
  return render_template(
    "horloge.html", 
    heure = local_time.tm_hour, 
    minute = local_time.tm_min, 
    seconde = local_time.tm_sec
  )



### Template avec structures de contrôle

@app.route("/semaine")
def days():
  local_time = time.localtime()
  day_list = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
  until_we = day_list[local_time.tm_wday:]
  return render_template("semaine.html", nb_jours = len(until_we), jours = until_we)



### Adresses variables

@app.route("/mois_<int:month>")
def months(month):
  if month < 1 or month > 12:
    return render_template("erreur_mois.html", num_mois = month)
  else:
    month_list = ["janvier", "fevrier", "mars", "avril", "mai", "juin", 
      "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    name = month_list[month - 1]
    return render_template("mois.html", num_mois = month, nom_mois = name)



### Formulaires POST et GET

# Page contenant le formulaire POST
@app.route("/formulaire")
def form():
  return render_template("formulaire.html")

# Récupération des données du formulaire POST
@app.route("/traiter_demande", methods = ['POST'])
def process_form():
  name = request.form.get("nom",None)
  add_type = request.form.get("type_ajout",None)
  if not name or not add_type:
    return redirect(url_for("form"))
  return render_template("recu_formulaire.html", nom = name, type_ajout = add_type)

# Page contenant le formularie GET
@app.route("/recherche")
def search():
  return render_template("recherche.html")

# Récupération des données du formulaire GET
@app.route("/resultats")
def search_results():
  start = request.args.get("debut",None)
  end = request.args.get("fin",None)
  try:
    start = int(start)
    end = int(end)
  except:
    return redirect(url_for("search"))
  month_list = ["janvier", "fevrier", "mars", "avril", "mai", "juin", 
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
  month_list = month_list[start-1:end]
  return render_template("resultats.html", liste = month_list)



### Utilisation des sessions

# Page de connexion
@app.route("/connexion")
def login():
  if "pseudo" in session:
    return redirect(url_for("welcome"))
  return render_template("connexion.html")

# Création de la variable de session indiquant que la connexion s'est bien faite
@app.route("/verification", methods = ['POST'])
def connect():
  pseudo = request.form.get("pseudo",None)
  if not pseudo:
    return redirect(url_for("login"))
  session["pseudo"] = pseudo
  return redirect(url_for("welcome"))

# Page d'accueil, accessible seulement si la variable de session existe
@app.route("/accueil")
def welcome():
  if "pseudo" in session:
    return render_template("accueil.html")
  return redirect(url_for("login"))

# Deconnexion, suppression de la variable de session
@app.route("/deconnexion")
def logout():
  if "pseudo" in session:
    session.pop("pseudo")
  return redirect(url_for("login"))

if __name__ == '__main__':
  app.run()

