---<Importation de la base de données Nuage>---

--\i C:/Users/yacin/Documents/GitHub/Projet-Nuage/dump-nuage-HAMADOUCHE-GAVAU--PELISSIER.sql--

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
DROP VIEW IF EXISTS Boutique;
DROP VIEW IF EXISTS JoueurPossede;
DROP VIEW IF EXISTS JoueurPartage;
DROP VIEW IF EXISTS CommentaireJeu;
DROP VIEW IF EXISTS TauxCompletion;

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
        d.nomEntreprise AS developpeur,
        ed.nomEntreprise AS editeur,
        j.description_Jeu AS description,
        j.image_path,
        STRING_AGG(DISTINCT g.nomGenre, ', ') AS genres,
        ROUND(AVG(c.note), 0) AS noteMoyenne
    FROM 
        Jeu AS j
        LEFT JOIN JeuGenre AS jg ON j.idJeu = jg.idJeu
        LEFT JOIN Genre AS g ON jg.idGenre = g.idGenre
        LEFT JOIN Entreprise AS d ON j.idDeveloppeur = d.idEntreprise
        LEFT JOIN Entreprise AS ed ON j.idEditeur = ed.idEntreprise
        LEFT JOIN Commentaire AS c ON j.idJeu = c.idJeu
    GROUP BY 
        j.idJeu, j.titre, j.prix, j.date_de_sortie, j.pegi, j.idDeveloppeur, j.idEditeur, j.description_Jeu, j.image_path, d.nomEntreprise, ed.nomEntreprise
);


CREATE VIEW JoueurAmis AS
(
    SELECT 
        j1.idJoueur AS idJoueur1,
        j2.idJoueur AS idJoueur2,
        j1.pseudo AS pseudo1,
        j2.pseudo AS pseudo2
    FROM 
        Joueur AS j1
        JOIN Amitie AS a ON j1.idJoueur = a.idJoueur1
        JOIN Joueur AS j2 ON a.idJoueur2 = j2.idJoueur
    UNION
    SELECT 
        j2.idJoueur AS idJoueur1,
        j1.idJoueur AS idJoueur2,
        j2.pseudo AS pseudo1,
        j1.pseudo AS pseudo2
    FROM 
        Joueur AS j1
        JOIN Amitie AS a ON j1.idJoueur = a.idJoueur1
        JOIN Joueur AS j2 ON a.idJoueur2 = j2.idJoueur
);

---<Insertions>---

INSERT INTO Joueur VALUES (1, 'yacine20005', '$2b$12$koVR5g1jNH/PvGrHNTlJoOTRN6wQk/ckllO3Q8owR19oBbAql2/US', 'Yacine', 'ya.hamadouche@gmail.com', '2005-12-24', 55.00); --Joueur 1--
INSERT INTO Joueur VALUES (2, 'SkY', '$2b$12$VUvcWjC9aQ64sabB443xh.LLmzdXFPq5o0l71CESvcup9tNLgnt1C', 'Liam', 'liam@outlook.com', '2005-12-16', 2546.00); --Joueur 2-- --Liam est riche grâce au CROUS--
INSERT INTO Joueur VALUES (3, 'playerOne', '$2b$12$koVR5g1jNH/PvGrHNTlJoOTRN6wQk/ckllO3Q8owR19oBbAql2/US', 'John', 'john@example.com', '1990-01-01', 100.00); --Joueur 3--
INSERT INTO Joueur VALUES (4, 'gamerGirl', '$2b$12$koVR5g1jNH/PvGrHNTlJoOTRN6wQk/ckllO3Q8owR19oBbAql2/US', 'Jane', 'jane@example.com', '1992-02-02', 200.00); --Joueur 4--
INSERT INTO Joueur VALUES (5, 'proGamer', '$2b$12$koVR5g1jNH/PvGrHNTlJoOTRN6wQk/ckllO3Q8owR19oBbAql2/US', 'Alex', 'alex@example.com', '1988-03-03', 300.00); --Joueur 5--
INSERT INTO Joueur VALUES (6, 'noobMaster', '$2b$12$koVR5g1jNH/PvGrHNTlJoOTRN6wQk/ckllO3Q8owR19oBbAql2/US', 'Chris', 'chris@example.com', '2008-04-04', 400.00); --Joueur 6--
INSERT INTO Joueur VALUES (7, 'eliteGamer', '$2b$12$koVR5g1jNH/PvGrHNTlJoOTRN6wQk/ckllO3Q8owR19oBbAql2/US', 'Sam', 'sam@example.com', '1993-05-05', 500.00); --Joueur 7--

INSERT INTO Entreprise VALUES (1, 'CD Projekt Red', 'Pologne'); --CD Projekt Red est une entreprise polonaise--
INSERT INTO Entreprise VALUES (2, 'Criterion', 'Royaume-Uni'); --Criterion est une entreprise britannique--
INSERT INTO Entreprise VALUES (3, 'EA', 'États-Unis'); --EA est une entreprise américaine--
INSERT INTO Entreprise VALUES (4, 'Rocksteady Studios', 'Royaume-Uni'); --Rocksteady est une entreprise britannique--
INSERT INTO Entreprise VALUES (5, 'Warner Bros Games', 'États-Unis'); --Warner Bros est une entreprise americaine--
INSERT INTO Entreprise VALUES (6, 'Kunos Simulazioni', 'Italie'); --Kunos Simulazioni est une entreprise italienne--
INSERT INTO Entreprise VALUES (7, 'GSC Game World', 'Ukraine'); --GSC Game World est une entreprise ukrainienne--
INSERT INTO Entreprise VALUES (8, 'Bungie', 'États-Unis'); --Bungie est une entreprise américaine--

INSERT INTO Genre VALUES (1, 'RPG'); --Définition du genre RPG--
INSERT INTO Genre VALUES (2, 'Course'); --Définition du genre Course--
INSERT INTO Genre VALUES (3, 'Action'); --Définition du genre Action--
INSERT INTO Genre VALUES (4, 'Tir'); --Définition du genre Tir--
INSERT INTO Genre VALUES (5, 'Looter'); --Définition du genre Looter--

INSERT INTO Jeu VALUES (1, 'Cyberpunk 2077', 69.99, '2020-12-10', 18, 1, 1, 'Cyberpunk 2077 est un JDR d''action-aventure en monde ouvert, qui se déroule à Night City, une mégalopole futuriste et sombre, obsédée par le pouvoir, la séduction et les modifications corporelles.', '/images/cyberpunk2077.jpg'); --CD Projekt Red est le développeur et l'éditeur du jeu en même temps--
INSERT INTO Jeu VALUES (2, 'Need for speed Unbound', 39.99, '2022-11-29', 12, 2, 3, 'Pour atteindre le sommet, pas le droit à l’erreur ! Défiez la police et participez aux qualifications pour participer au Grand, la course de rue ultime. Sublimez votre garage avec des voitures ultra personalisées, et brillez grâce à votre style unique.', '/images/nfs_unbound.jpg'); --Criterion est le développeur et EA est l'éditeur du jeu --
INSERT INTO Jeu VALUES (3, 'Batman Arkham Knight', 59.99, '2015-06-23', 18, 4, 5, 'Enfilez le masque alors que le Chevalier noir s''aventure dans l''ultime chapitre de la trilogie Arkham par Rocksteady. Les joueurs incarneront le plus grand détective du monde comme jamais auparavant grâce à l''arrivée de la Batmobile et aux améliorations apportées à des éléments clés des précédents opus : le combat déchaîné, la furtivité, le scanner médico-légal et la navigation.', '/images/batman.jpg'); --Rocksteady est le développeur et Warner Bros est l'éditeur du jeu--
INSERT INTO Jeu VALUEs (4, 'Assetto Corsa Competizione', 39.99, '2019-05-29', 3, 6, 6, 'Assetto Corsa Competizione est le nouveau jeu vidéo officiel de la série Blancpain GT Series. Grâce à la qualité exceptionnelle de la simulation, vous pourrez vivre l''atmosphère de la GT3, et affronter des pilotes, des équipes, des voitures et des circuits officiels.', '/images/assetto_corsa.jpg'); --Kunos Simulazioni est le développeur et l'éditeur du jeu--
INSERT INTO Jeu VALUES (5, 'S.T.A.L.K.E.R. 2: Heart of Chornobyl', 59.99, '2024-11-20', 18, 7, 7, 'Partez explorer la vaste Zone d''exclusion de Tchornobyl et ses ennemis redoutables, ses anomalies mortelles et ses puissants artefacts. Découvrez votre propre histoire épique en vous frayant un chemin jusqu''au cœur de Tchornobyl.', '/images/stalker2.jpg'); --GSC Game World est le développeur et l'éditeur du jeu--
INSERT INTO Jeu VALUES (6, 'Destiny 2', 0.00, '2019-10-01', 16, 8, 8, 'Plongez dans l''univers de Destiny 2 pour explorer les mystères de notre système solaire, et découvrez les combats réactifs de ce jeu de tir à la première personne. Débloquez de puissantes capacités élémentaires et collectionnez de l''équipement unique pour personnaliser le look de votre Gardien et votre style de jeu. Découvrez les cinématiques de Destiny 2, des missions en coopération corsées, et toute une variété de modes en JcJ en solo ou avec vos amis. Téléchargez gratuitement dès aujourd''hui et écrivez votre légende dans les étoiles.', '/images/destiny2.jpg'); --Bungie est le développeur et l'éditeur du jeu--

INSERT INTO JeuGenre VALUES (1, 1); --Cyberpunk 2077 est un RPG--
INSERT INTO JeuGenre VALUES (2, 2); --NFS Unbound est un jeu de course--
INSERT INTO JeuGenre VALUES (1, 3); --Cyberpunk 2077 est un jeu d'action--
INSERT INTO JeuGenre VALUES (3, 3); --Batman est un jeu d'action--
INSERT INTO JeuGenre VALUES (4, 2); --Assetto Corsa est un jeu de course--
INSERT INTO JeuGenre VALUES (5, 1); --S.T.A.L.K.E.R. 2 est un RPG--
INSERT INTO JeuGenre VALUES (5, 3); --S.T.A.L.K.E.R. 2 est un jeu d'action--
INSERT INTO JeuGenre VALUES (6, 3); -- Destiny 2 est un jeu d'action
INSERT INTO JeuGenre VALUES (6, 4); -- Destiny 2 est un jeu de tir
INSERT INTO JeuGenre VALUES (6, 5); -- Destiny 2 est un jeu de loot

INSERT INTO Succes VALUES (1, 1, 'Braquage Konpeki Plaza', 'Vous avez eu ce que vous vouliez mais à quel prix ?'); --Succès du jeu Cyberpunk 2077--
INSERT INTO Succes VALUES (2, 2, 'Insaisissable', 'Échappez à une poursuite policière en Alerte 5 au volant d’une voiture A+'); --Succès du jeu NFS Unbound--
INSERT INTO Succes VALUES (3, 2, 'Le roi de la route', 'Remportez toutes les courses de rue'); --Succès du jeu NFS Unbound--
INSERT INTO Succes VALUES (4, 2, 'Le roi du drift', 'Remportez toutes les courses de drift'); --Succès du jeu NFS Unbound--
INSERT INTO Succes VALUES (5, 2, 'Le roi de la déliquence', 'Echappez à 10 poursuites policières'); --Succès du NFS Unbound--
INSERT INTO Succes VALUES (6, 3, 'Le chevalier noir', 'Terminez le jeu en difficulté Chevalier Noir'); --Succès du jeu Batman--
INSERT INTO Succes VALUES (7, 4, 'Le roi de la piste', 'Remportez toutes les courses de la série Blancpain GT Series'); --Succès du jeu Assetto Corsa--
INSERT INTO Succes VALUES (8, 4, 'Le roi de la nuit', 'Remportez une course de nuit'); --Succès du jeu Assetto Corsa--
INSERT INTO Succes VALUES (9, 5, 'Survivant de Tchornobyl', 'Terminez le jeu en difficulté maximale'); --Succès du jeu S.T.A.L.K.E.R. 2--
INSERT INTO Succes VALUES (10, 5, 'Explorateur de la Zone', 'Découvrez tous les lieux d''intérêt'); --Succès du jeu S.T.A.L.K.E.R. 2--
INSERT INTO Succes VALUES (11, 6, 'Premier pas', 'Terminez la dernière mission.');
INSERT INTO Succes VALUES (12, 6, 'Gardien aguerri', 'Atteignez le niveau maximum.');
INSERT INTO Succes VALUES (13, 6, 'Maître des raids', 'Terminez tous les raids.');

INSERT INTO JoueurSucces VALUES (1, 1, '2020-12-27'); --Yacine a obtenu le succès "Braquage Konpeki Plaza" le 27 décembre 2020--
INSERT INTO JoueurSucces VALUES (1, 2, '2022-12-01'); --Yacine a obtenu le succès "Insaisissable" le 1er décembre 2022--
INSERT INTO JoueurSucces VALUES (1, 4, '2022-12-01'); --Yacine a obtenu le succès "Le roi du drift" le 1er décembre 2022--
INSERT INTO JoueurSucces VALUES (1, 10, '2024-12-12'); --Yacine a obtenu le succès "Explorateur de la Zone" le 12 décembre 2024--
INSERT INTO JoueurSucces VALUES (1, 11, '2022-02-12'); --Yacine a obtenu le succès "Premier pas" le 12 février 2022--
INSERT INTO JoueurSucces VALUES (1, 12, '2022-04-01'); --Yacine a obtenu le succès "Gardien aguerri" le 1er avril 2022--
INSERT INTO JoueurSucces VALUES (1, 13, '2022-04-25');  --Yacine a obtenu le succès "Maître des raids" le 25 avril 2022--

INSERT INTO Commentaire VALUES (1, 17, 'J''ai versé une larme à la fin du jeu vraiment un banger vidéoludique', 1, 1); --Commentaire du joueur 1 sur le jeu 1--
INSERT INTO Commentaire VALUES (2, 19, 'Le jeu est parfait, mais beaucoup trop de scènes obscènes', 1, 2); --Commentaire du joueur 2 sur le jeu 1--
INSERT INTO Commentaire VALUES (3, 14, 'J''ai adoré le jeu mais les voitures sont très désequilibrés en multijoueur...', 2, 1); --Commentaire du joueur 1 sur le jeu 2--
INSERT INTO Commentaire VALUES (4, 18, 'Je me suis senti dans la peau du chevalier noir pendant toute la durée du jeu, je recommande vivement pour tous les fans de la licence.', 3, 2); --Commentaire du joueur 2 sur le jeu 3 --
INSERT INTO Commentaire VALUES (5, 20, 'Le jeu est très réaliste, mais les graphismes sont un peu décevants...', 4, 1); --Commentaire du joueur 3 sur le jeu 1--
INSERT INTO Commentaire VALUES (6, 19, 'Un jeu incroyable avec une atmosphère unique, je recommande vivement.', 5, 1); --Commentaire du joueur 1 sur le jeu S.T.A.L.K.E.R. 2--
INSERT INTO Commentaire VALUES (7, 20, 'Un jeu incroyable avec une communauté active et un contenu régulier.', 6, 1); --Commentaire du joueur 1 sur le jeu Destiny 2--
INSERT INTO Commentaire VALUES (8, 6, 'Le jeu est mauvais et les microtransactions sont trop présentes.', 6, 2); --Commentaire du joueur 2 sur le jeu Destiny 2--

INSERT INTO Transaction_user VALUES (1, 1, 1, 69.99, '2020-12-26', 'Achat du jeu Cyberpunk 2077'); --Transaction d'achat du jeu Cyberpunk 2077 par le joueur 1--
INSERT INTO Transaction_user VALUES (2, 1, 2, 39.99, '2022-11-17', 'Précommande NFS Unbound'); --Transaction de précommande du jeu NFS Unbound par le joueur 1--
INSERT INTO Transaction_user VALUES (3, 2, 3, 59.99, '2024-12-11', 'Achat du jeu Batman Arkham Knight'); --Transaction d'achat du jeu Batman par le joueur 2--
INSERT INTO Transaction_user VALUES (4, 1, 4, 39.99, '2022-12-01', 'Achat du jeu Assetto Corsa Competizione'); --Transaction d'achat du jeu Assetto Corsa par le joueur 1--
INSERT INTO Transaction_user VALUES (5, 1, 5, 59.99, '2024-11-20', 'Achat du jeu S.T.A.L.K.E.R. 2: Heart of Chornobyl'); --Transaction d'achat du jeu S.T.A.L.K.E.R. 2 par le joueur 1--
INSERT INTO Transaction_user VALUES (6, 1, 6, 0.00, '2019-10-01', 'Téléchargement de Destiny 2'); --Transaction de téléchargement du jeu Destiny 2 par le joueur 1--

INSERT INTO JoueurJeu VALUES (1, 1, '2020-12-26'); --Yacine a acheté Cyberpunk 2077 le 26 décembre 2020--
INSERT INTO JoueurJeu VALUES (1, 2, '2022-11-17'); --Yacine a acheté NFS Unbound le 17 novembre 2022--
INSERT INTO JoueurJeu VALUES (2, 3, '2024-12-11'); --Liam a acheté Batman le 11 décembre 2024--
INSERT INTO JoueurJeu VALUES (1, 4, '2022-12-01'); --Yacine a acheté Assetto Corsa le 1er décembre 2022--
INSERT INTO JoueurJeu VALUES (1, 5, '2024-11-20'); --Yacine a acheté S.T.A.L.K.E.R. 2 le 20 novembre 2024--
INSERT INTO JoueurJeu VALUES (1, 6, '2019-10-01'); --Yacine a téléchargé Destiny 2 le 1er octobre 2019--

INSERT INTO Amitie VALUES (1, 2); --Yacine et Liam sont amis--
INSERT INTO Amitie VALUES (1, 7); --Yacine et Sam sont amis--
INSERT INTO Amitie VALUES (2, 4); --Liam et Jane sont amis--

INSERT INTO Partage VALUES (1, 2, 1); --Yacine a partager avec Liam une expérience vidéoludique sans précédent (Cyberpunk 2077)--
INSERT INTO Partage VALUES (2, 1, 3); --Liam a partager avec Yacine Batman Arkham Knight--