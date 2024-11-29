import psycopg2
import psycopg2.extras

def connect():
    conn = psycopg2.connect(
        dbname='nuage',
        user='yacine',  # Remplacez par votre nom d'utilisateur PostgreSQL
        password='yacine',  # Remplacez par votre mot de passe PostgreSQL
        host='localhost',
        port='5432',
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn