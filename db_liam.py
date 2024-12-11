import psycopg2.extras

def connect():
    conn = psycopg2.connect(
        dbname='nuage',
        user='sky',  # Remplacez par votre nom d'utilisateur PostgreSQL
        password='sky',  # Remplacez par votre mot de passe PostgreSQL
        host='localhost',
        port='5432',
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn