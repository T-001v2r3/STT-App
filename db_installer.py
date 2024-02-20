import os
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import argparse

load_dotenv()  

def database_exists(conn, db_name):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    return cur.fetchone() is not None

def table_exists(conn, table_name):
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = %s
    """, (table_name,))
    return cur.fetchone() is not None

def create_database(conn, db_name):
    if not database_exists(conn, db_name):
        conn.autocommit = True  # set connection to autocommit mode
        cur = conn.cursor()
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database {db_name} created successfully")
    else:
        print(f"Database {db_name} already exists")

def create_table(conn, table_name):
    if not table_exists(conn, table_name):
        cur = conn.cursor()
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                EntryID SERIAL PRIMARY KEY,
                InputDateTime TIMESTAMP NOT NULL,
                AudioFileName TEXT NOT NULL,
                UserMetadata JSONB,
                PreprocessedText TEXT,
                AlertMetadata JSONB
            )
        """).format(sql.Identifier(table_name)))
        conn.commit()
        print(f"Table {table_name} created successfully")
    else:
        print(f"Table {table_name} already exists")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean', action='store_true', help='Delete the current database and create a new one')
    args = parser.parse_args()

    db_credentials = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
    }
    dbname = os.getenv('DB_NAME')
    print("DB host: ", db_credentials['host'])
    print("DB port: ", db_credentials['port'])
    print("DB user: ", db_credentials['user'])
    print("DB pass: ", db_credentials['password'])
    print("DB name: ", dbname)

    print("Attempting to connect to the PostgreSQL server...")
    conn = psycopg2.connect(**db_credentials)
    conn.autocommit = True
    if args.clean:
        print("Clean flag detected. Deleting and recreating the database...")
        conn.autocommit = True  # set connection to autocommit mode
        cur = conn.cursor()
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(dbname)))
        create_database(conn, dbname)
        print("Database created. Closing connection...")
        conn.close()
    else:
        print("Connected to the PostgreSQL server. Attempting to create database...")
        create_database(conn, dbname)
        print("Database created. Closing connection...")
        conn.close()

    print("Reconnecting to the new database...")
    db_credentials['dbname'] = dbname
    conn = psycopg2.connect(**db_credentials)
    if conn:
        print("Connected to the new database. Attempting to create table...")
        create_table(conn, dbname)
        print("Table created. Closing connection...")
        conn.close()

if __name__ == "__main__":
    main()
