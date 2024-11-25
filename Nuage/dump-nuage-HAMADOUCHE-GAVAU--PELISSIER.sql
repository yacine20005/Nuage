---<Suppression des tables et vues si elles existent>---

DROP TABLE IF EXISTS Jeu CASCADE;
DROP TABLE IF EXISTS Genre CASCADE;
DROP TABLE IF EXISTS Entreprise CASCADE;
DROP TABLE IF EXISTS Succes CASCADE;
DROP TABLE IF EXISTS Commentaire CASCADE;
DROP TABLE IF EXISTS Joueur CASCADE;
DROP TABLE IF EXISTS Transaction_user CASCADE;
DROP TABLE IF EXISTS Amitie CASCADE;
DROP TABLE IF EXISTS Partage CASCADE;
DROP TABLE IF EXISTS JoueurJeu CASCADE;
DROP TABLE IF EXISTS JoueurSucces CASCADE;
DROP TABLE IF EXISTS JeuGenre CASCADE;
DROP VIEW IF EXISTS RapportVentes;

---<Tables>---

CREATE TABLE Joueur (
    idJoueur SERIAL,
    pseudo VARCHAR(50) CHECK (LENGTH(pseudo) BETWEEN 3 AND 16) NOT NULL UNIQUE, --LENGTH permet d'obtenir la taille du varchar--
    mot_de_passe VARCHAR(100) CHECK (LENGTH(mot_de_passe) >= 8) NOT NULL,
    nom VARCHAR(100),
    email VARCHAR(100) CHECK (email LIKE '%@%' AND email LIKE '%.%') NOT NULL, --On vérifie que l'email contient un "@" et un "." pour être valide--
    date_naissance DATE,
    solde DECIMAL(10, 2) CHECK (solde >= 0), --On vérifie que le joueur n'est pas endetté--
    PRIMARY KEY (idJoueur)
);

CREATE TABLE Entreprise (
    idEntreprise SERIAL,
    nomEntreprise VARCHAR(100) NOT NULL,
    pays VARCHAR(100) NOT NULL,
    PRIMARY KEY (idEntreprise)
);

CREATE TABLE Genre (
    idGenre SERIAL,
    nomGenre VARCHAR(100) NOT NULL,
    PRIMARY KEY (idGenre)
);

CREATE TABLE Jeu (
    idJeu SERIAL,
    titre VARCHAR(100) NOT NULL,
    prix DECIMAL(10, 2) CHECK (prix >= 0) NOT NULL,
    date_de_sortie DATE DEFAULT CURRENT_DATE, --DEFAULT CURRENT_DATE permet de mettre la date actuelle par défaut si aucune date n'est renseignée--
    pegi INT CHECK (pegi BETWEEN 3 AND 18),
    idDeveloppeur INT,
    idEditeur INT,
    description_Jeu TEXT,
    image_path VARCHAR(255), --On stocke le chemin de l'image du jeu pour l'afficher dans l'application--
    PRIMARY KEY (idJeu),
    FOREIGN KEY (idDeveloppeur) REFERENCES Entreprise(idEntreprise),
    FOREIGN KEY (idEditeur) REFERENCES Entreprise(idEntreprise)
);

CREATE TABLE Succes (
    idSucces SERIAL,
    idJeu INT,
    intitule VARCHAR(100) NOT NULL,
    description_Succes TEXT,
    PRIMARY KEY (idSucces),
    FOREIGN KEY (idJeu) REFERENCES Jeu(idJeu),
    CONSTRAINT unique_succes UNIQUE (idJeu, intitule) --On vérifie qu'un succès n'est pas dupliqué pour un jeu donné--
); 

CREATE TABLE Commentaire (
    idCommentaire SERIAL,
    note INT CHECK (note BETWEEN 0 AND 20) NOT NULL, --On vérifie que la note est bien comprise entre 0 et 20--
    texteCommentaire TEXT NOT NULL, 
    idJeu INT,
    idJoueur INT,
    PRIMARY KEY (idCommentaire),
    FOREIGN KEY (idJeu) REFERENCES Jeu(idJeu),
    FOREIGN KEY (idJoueur) REFERENCES Joueur(idJoueur),
    CONSTRAINT unique_commentaire UNIQUE (idJeu, idJoueur) --On vérifie qu'un joueur ne peut pas commenter plusieurs fois le même jeu--
);

CREATE TABLE Transaction_user (
    idTransaction SERIAL,
    idJoueur INT,
    idJeu INT,
    montant DECIMAL(10, 2) CHECK (montant >= 0) NOT NULL, --On vérifie que le joueur ne gagne pas d'argent en achetant un jeu--
    date_transaction DATE DEFAULT CURRENT_DATE,
    objet_transaction VARCHAR(50) DEFAULT 'Inconnu', --On met "Inconnu" par défaut si l'objet de la transaction n'est pas renseigné--
    PRIMARY KEY (idTransaction),
    FOREIGN KEY (idJoueur) REFERENCES Joueur(idJoueur),
    FOREIGN KEY (idJeu) REFERENCES Jeu(idJeu)
);

CREATE TABLE Amitie (
    idJoueur1 INT,
    idJoueur2 INT,
    PRIMARY KEY (idJoueur1, idJoueur2),
    FOREIGN KEY (idJoueur1) REFERENCES Joueur(idJoueur),
    FOREIGN KEY (idJoueur2) REFERENCES Joueur(idJoueur),
    CONSTRAINT check_doublon_amitie CHECK (idJoueur1 < idJoueur2) --On vérifie que l'idJoueur1 est plus petit que l'idJoueur2 pour éviter les doublons éventuelles--
);

CREATE TABLE Partage (
    idJoueur1 INT,
    idJoueur2 INT,
    idJeu INT,
    PRIMARY KEY (idJoueur1, idJoueur2, idJeu),
    FOREIGN KEY (idJoueur1) REFERENCES Joueur(idJoueur),
    FOREIGN KEY (idJoueur2) REFERENCES Joueur(idJoueur),
    FOREIGN KEY (idJeu) REFERENCES Jeu(idJeu),
    CONSTRAINT check_doublon_partage CHECK (idJoueur1 < idJoueur2), --On vérifie que l'idJoueur1 est plus petit que l'idJoueur2 pour éviter les doublons éventuelles--
    CONSTRAINT check_same_joueur_partage CHECK (idJoueur1 != idJoueur2), --On vérifie que l'idJoueur1 est différent de l'idJoueur2 parce qu'on ne peut pas partager un jeu avec soi-même...--
    CONSTRAINT unique_partage UNIQUE (idJoueur1, idJeu) --On vérifie que le joueur 1 n'a pas déjà partagé ce jeu--
    --CONSTRAINT check_amitie_partage CHECK ((idJoueur1, idJoueur2) IN (SELECT idJoueur1, idJoueur2 FROM Amitie)), --On vérifie que les joueurs sont bien amis pour partager un jeu--
    --CONSTRAINT check_jeu_appartient CHECK (idJeu IN (SELECT idJeu FROM JoueurJeu WHERE idJoueur = idJoueur1)), --On vérifie que le jeu partagé appartient bien au joueur qui le partage--
    --Les contraintes check_amitie_partage et check_jeu_appartient ne fonctionnent pas nous devrons faire en sorte que ces contraintes soit vérifiées au niveau applicatif avec Python--
);

CREATE TABLE JoueurJeu (
    idJoueur INT,
    idJeu INT,
    date_achat DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (idJoueur, idJeu),
    FOREIGN KEY (idJoueur) REFERENCES Joueur(idJoueur),
    FOREIGN KEY (idJeu) REFERENCES Jeu(idJeu)
);

CREATE TABLE JoueurSucces (
    idJoueur INT,
    idSucces INT,
    date_obtention DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (idJoueur, idSucces),
    FOREIGN KEY (idJoueur) REFERENCES Joueur(idJoueur),
    FOREIGN KEY (idSucces) REFERENCES Succes(idSucces)
);

CREATE TABLE JeuGenre (
    idJeu INT,
    idGenre INT,
    PRIMARY KEY (idJeu, idGenre),
    FOREIGN KEY (idJeu) REFERENCES Jeu(idJeu),
    FOREIGN KEY (idGenre) REFERENCES Genre(idGenre)
);

---<Vues>---

/*CREATE VIEW RapportVentes AS
(
SELECT 
    e.nomEntreprise AS Entreprise, --On récupère le nom de l'entreprise--
    t.date_transaction AS Date, --On récupère la date pour séparer les stats par date--
    COUNT(DISTINCT t.idTransaction) AS NombreVentes, --On compte le nombre de ventes différentes--
    COUNT(DISTINCT p.idJeu) AS NombrePrets, --On compte le nombre de prêts différents--
    SUM(t.montant) AS ChiffreAffaire, --On somme les montants des transactions pour obtenir le chiffre d'affaire total--
    AVG(c.note) AS NotationMoyenne --On calcule la moyenne des notes des commentaires pour obtenir la notation moyenne--
    --Manque les succès obtenus dans le jeu--
FROM 
    Jeu AS j
    JOIN Entreprise AS e ON j.idEditeur = e.idEntreprise
    LEFT JOIN Transaction_user AS t ON j.idJeu = t.idJeu
    LEFT JOIN Partage AS p ON j.idJeu = p.idJeu
    LEFT JOIN Commentaire AS c ON j.idJeu = c.idJeu
GROUP BY 
    e.nomEntreprise, t.date_transaction
);*/

CREATE VIEW RapportVentes AS
(
    SELECT 
        e.nomEntreprise AS Entreprise, --On récupère le nom de l'entreprise--
        t.date_transaction AS Date, --On récupère la date pour séparer les stats par date--
        COUNT(DISTINCT t.idTransaction) AS NombreVentes, --On compte le nombre de ventes différentes--
        COUNT(DISTINCT p.idJeu) AS NombrePrets, --On compte le nombre de prêts différents--
        SUM(t.montant) AS ChiffreAffaire, --On somme les montants des transactions pour obtenir le chiffre d'affaire total--
        AVG(c.note) AS NotationMoyenne --On calcule la moyenne des notes des commentaires pour obtenir la notation moyenne--
        --Manque les succès obtenus dans le jeu--
    FROM 
        Jeu AS j
        JOIN Entreprise AS e ON j.idEditeur = e.idEntreprise
        LEFT JOIN Transaction_user AS t ON j.idJeu = t.idJeu
        LEFT JOIN Partage AS p ON j.idJeu = p.idJeu
        LEFT JOIN Commentaire AS c ON j.idJeu = c.idJeu
    GROUP BY 
        e.nomEntreprise, t.date_transaction
);

CREATE VIEW Boutique AS 
(
    SELECT 
        j.idJeu,
        j.titre,
        j.prix,
        j.date_de_sortie,
        j.pegi,
        j.idDeveloppeur,
        j.idEditeur,
        j.description_Jeu,
        j.image_path,
        STRING_AGG(g.nomGenre, ', ') AS genres
    FROM 
        Jeu AS j
        JOIN JeuGenre AS jg ON j.idJeu = jg.idJeu
        JOIN Genre AS g ON jg.idGenre = g.idGenre
    GROUP BY 
        j.idJeu, j.titre, j.prix, j.date_de_sortie, j.pegi, j.idDeveloppeur, j.idEditeur, j.description_Jeu, j.image_path, g.nomGenre
);


---<Insertions>---

INSERT INTO Joueur VALUES (1, 'yacine20005', 'ScoobyHonda', 'Yacine', 'ya.hamadouche@gmail.com', '2005-12-24', 55.00); --Joueur 1--
INSERT INTO Joueur VALUES (2, 'SkY', 'Gael_ma_crush_92i', 'Liam', 'liam@outlook.com', '2005-12-16', 2546.00); --Joueur 2-- --Liam est riche grâce au CROUS--

INSERT INTO Entreprise VALUES (1, 'CD Projekt Red', 'Pologne'); --CD Projekt Red est une entreprise polonaise--
INSERT INTO Entreprise VALUES (2, 'Criterion', 'Royaume-Uni'); --Criterion est une entreprise britannique--
INSERT INTO Entreprise VALUES (3, 'EA', 'États-Unis'); --EA est une entreprise américaine--

INSERT INTO Genre VALUES (1, 'RPG'); --Définition du genre RPG--
INSERT INTO Genre VALUES (2, 'Course'); --Définition du genre Course--

INSERT INTO Jeu VALUES (1, 'Cyberpunk 2077', 69.99, '2020-12-10', 18, 1, 1, 'RPG dans un futur cyberpunk', '/images/cyberpunk2077.jpg'); --CD Projekt Red est le développeur et l'éditeur du jeu en même temps--
INSERT INTO Jeu VALUES (2, 'Need for speed Unbound', 39.99, '2022-11-29', 12, 2, 3, 'Jeu de course de rue', '/images/nfs_unbound.jpg'); --Criterion est le développeur et EA est l'éditeur du jeu --

INSERT INTO Succes VALUES (1, 1, 'Braquage Konpeki Plaza', 'Vous avez eu ce que vous vouliez mais à quel prix ?'); --Succès du jeu Cyberpunk 2077--
INSERT INTO Succes VALUES (2, 2, 'Insaisissable', 'Échappez à une poursuite policière en Alerte 5 au volant d’une voiture A+'); --Succès du jeu NFS Unbound--

INSERT INTO Commentaire VALUES (1, 17, 'J''ai versé une larme à la fin du jeu vraiment un banger vidéoludique', 1, 1); --Commentaire du joueur 1 sur le jeu 1--
INSERT INTO Commentaire VALUES (2, 19, 'Le jeu est parfait, mais beaucoup trop de scènes obscènes', 1, 2); --Commentaire du joueur 2 sur le jeu 1--
INSERT INTO Commentaire VALUES (3, 14, 'J''ai adoré le jeu mais les voitures sont très désequilibrés en multijoueur...', 2, 1); --Commentaire du joueur 1 sur le jeu 2--

INSERT INTO Transaction_user VALUES (1, 1, 1, 69.99, '2020-12-26', 'Achat du jeu Cyberpunk 2077'); --Transaction d'achat du jeu Cyberpunk 2077 par le joueur 1--
INSERT INTO Transaction_user VALUES (2, 1, 2, 39.99, '2022-11-17', 'Précommande NFS Unbound'); --Transaction de précommande du jeu NFS Unbound par le joueur 1--

INSERT INTO Amitie VALUES (1, 2); --Yacine et Liam sont amis--

INSERT INTO Partage VALUES (1, 2, 1); --Yacine a partager avec Liam une expérience vidéoludique sans précédent (Cyberpunk 2077)--

INSERT INTO JoueurJeu VALUES (1, 1, '2020-12-26'); --Yacine a acheté Cyberpunk 2077 le 26 décembre 2020--

INSERT INTO JoueurSucces VALUES (1, 1, '2020-12-27'); --Yacine a obtenu le succès "Braquage Konpeki Plaza" le 27 décembre 2020--
INSERT INTO JoueurSucces VALUES (1, 2, '2022-12-01'); --Yacine a obtenu le succès "Insaisissable" le 1er décembre 2022--

INSERT INTO JeuGenre VALUES (1, 1); --Cyberpunk 2077 est un RPG--
INSERT INTO JeuGenre VALUES (2, 2); --NFS Unbound est un jeu de course--