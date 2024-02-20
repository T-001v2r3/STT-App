import psycopg2
from psycopg2 import Error

def create_connection():
    conn = None;
    try:
        print("Attempting to connect to PostgreSQL database...")
        conn = psycopg2.connect(
            host='34.163.172.208',
            port='5432',
            user='postgres',
            password='12345',
            dbname='postgres'
        )
        if conn:
            print('Connected to PostgreSQL database')
    except Error as e:
        print("Error occurred while connecting to database:", e)
    return conn

def create_database(conn, db_name):
    try:
        print(f"Attempting to create database {db_name}...")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"Database {db_name} created successfully")
    except Error as e:
        print(f"Error occurred while creating database {db_name}:", e)

def create_table(conn, table_name):
    try:
        print(f"Attempting to create table {table_name}...")
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                EntryID SERIAL PRIMARY KEY,
                InputDateTime TIMESTAMP NOT NULL,
                AudioFileName TEXT NOT NULL,
                UserMetadata JSONB,
                PreprocessedText TEXT,
                AlertMetadata JSONB
            )
        """)
        print(f"Table {table_name} created successfully")
    except Error as e:
        print(f"Error ocurred while creating table {table_name}:", e)

def main():
    conn = create_connection()
    if conn:
        create_database(conn, 'your_database')
        conn.close()
    else:
        print("Unable to create database due to connection error.")

    print("Reconnecting to the new database...")
    conn = psycopg2.connect(
        host='34.163.172.208',
        port='5432',
        user='postgres',
        password='12345',
        dbname='postgres'
    )
    if conn:
        create_table(conn, 'your_table')
        conn.close()
    else:
        print("Unable to create table due to connection error.")

if __name__ == '__main__':
    main()
