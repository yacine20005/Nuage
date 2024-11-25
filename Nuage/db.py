import psycopg2
import psycopg2.extras

def connect():
    conn = psycopg2.connect(
        host = 'sqledu.univ-eiffel.fr',
        dbname = 'zelia_db', # nom de votre base de données
        password = 'miaou18', # mot de passe de la base
        cursor_factory = psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn