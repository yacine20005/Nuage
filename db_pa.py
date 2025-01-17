import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

PGHOST = os.getenv('PGHOST')
PGDATABASE = os.getenv('PGDATABASE')
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')

def connect():
    conn = psycopg2.connect(
        dbname=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
        host=PGHOST,
        port='5432',
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn