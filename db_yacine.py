import psycopg2.extras

def connect():
    conn = psycopg2.connect(
        dbname='nuage',
        user='yacine',
        password='yacine',
        host='localhost',
        port='5432',
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn