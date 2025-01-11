# Nuage

## Introduction

Nuage est une application web de gestion de jeux vidéo. Elle permet aux utilisateurs de consulter, acheter, partager et commenter des jeux vidéo. Les utilisateurs peuvent également gérer leur profil, ajouter des amis et suivre leurs succès dans les jeux.

## Installation

Pour installer et exécuter le projet localement, suivez les étapes ci-dessous :

1. Clonez le dépôt GitHub :
   ```bash
   git clone https://github.com/yacine20005/Nuage.git
   cd Projet-Nuage
   ```

2. Créez un environnement virtuel et activez-le :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
   ```

3. Configurez la base de données PostgreSQL en utilisant le fichier `dump-nuage-HAMADOUCHE-GAVAU--PELISSIER.sql` fourni :
   ```bash
   psql -U <votre_utilisateur> -d <votre_base_de_donnees> -f dump-nuage-HAMADOUCHE-GAVAU--PELISSIER.sql
   ```

4. Exécutez l'application :
   ```bash
   flask run
   ```

## Usage

Une fois l'application en cours d'exécution, vous pouvez accéder aux fonctionnalités suivantes :

- **Boutique** : Parcourez et achetez des jeux vidéo.
- **Recherche** : Recherchez des jeux par titre, genre, développeur ou éditeur.
- **Profil** : Gérez votre profil, consultez vos jeux possédés, vos succès et vos amis.
- **Partage** : Partagez des jeux avec vos amis.
- **Commentaires** : Commentez les jeux et lisez les commentaires des autres utilisateurs.

Pour plus de détails sur chaque fonctionnalité, consultez le code source et les commentaires dans les fichiers Python et HTML.
