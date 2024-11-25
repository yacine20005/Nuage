import psycopg2
import psycopg2.extras

def connect():
    conn = psycopg2.connect(
        dbname='dump-nuage-HAMADOUCHE-GAVAU--PELISSIER',
        user='votre_nom_utilisateur',  # Remplacez par votre nom d'utilisateur PostgreSQL
        password='',  # Remplacez par votre mot de passe PostgreSQL
        host='localhost',
        port='5432',
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn