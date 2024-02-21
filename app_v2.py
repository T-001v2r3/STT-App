from flask import Flask, request
from datetime import datetime
#from google.cloud import speech
import os
import logging
from threading import Thread
# db stuff
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import json


# Set up logging
logging.basicConfig(filename='log.txt', level=logging.INFO, 
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def log_action(action):
    logging.info(action)

app = Flask(__name__)

#def process_audio_file(filename):
#    client = speech.SpeechClient()
#
#    with open(filename, 'rb') as audio_file:
#        audio = speech.RecognitionAudio(content=audio_file.read())
#    config = speech.RecognitionConfig(
#        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
#        sample_rate_hertz=16000,
#        # this needs to be a config param from client
#        language_code="en-US",
#    )
#
#    response = client.recognize(config=config, audio=audio)
#
#    ## Process the response...
#    for result in response.results:
#        print(result.alternatives[0].transcript)
#
#    # save on db path for the audio data
#

# this function will add to the table the new entry each one on each field
def db_entry_add(conn, filename, timestamp, user_metadata):
    print("Start Entry added to the table")
    try:
        cur = conn.cursor()
        dbname = os.getenv('DB_NAME')
        if dbname is None:
            print("DB_NAME environment variable is not set")
            return
        # Convert the user_metadata set to a list and then to a JSON string
        user_metadata_json = json.dumps(list(user_metadata))
        cur.execute(sql.SQL("""
            INSERT INTO {} (InputDateTime, AudioFileName, UserMetadata)
            VALUES (%s, %s, %s)
        """).format(sql.Identifier(dbname)), (timestamp, filename, user_metadata_json))
    except Exception as e:
        print("Error executing SQL query: ", e)
        return
    try:
        conn.commit()
    except Exception as e:
        print("Error committing transaction: ", e)
        return
    print("Completed Entry added to the table")

def create_db_entry(filename, timestamp, user_metadata):
    db_credentials = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'dbname': os.getenv('DB_NAME'),
    }
    print("DB host: ", db_credentials['host'])
    print("DB port: ", db_credentials['port'])
    print("DB user: ", db_credentials['user'])
    print("DB pass: ", db_credentials['password'])
    print("DB name: ", db_credentials['dbname'])

    print("Attempting to connect to the database...")
    conn = psycopg2.connect(**db_credentials)
    if conn:
        print("Connected to the new database. Attempting to add entry...")
        print("conn: ", conn)
        print("filename: ", filename)
        print("timestamp: ", timestamp)
        db_entry_add(conn, filename, timestamp, {1})
        print("Table created. Closing connection...")
        conn.close()

@app.route('/upload', methods=['POST'])
def upload():
    # audio fetched from browser
    audio_file = request.files['audio']

    # current date and time
    now = datetime.now()
    # name files audio_Y_M_D_h_m_s.ogg
    filename = 'audio_{}.webm'.format(now.strftime('%Y_%m_%d_%H_%M_%S'))
    print("filename")
    # verify if file already exists, if true rename
    i = 1
    while os.path.exists(filename):
        name, ext = os.path.splitext(filename)
        filename = '{}_{}{}'.format(name, i, ext)
        i += 1
    print("filename: ", filename)
    audio_file.save(filename)

    # create a log file with client id's if possible
    log_action('Saved file: {}'.format(filename))
    create_db_entry(filename, now, {1})
    # save on db the log for each alert

    # Start processing the file in a separate thread
    #thread = Thread(target=process_audio_file, args=(filename,))
    #thread.start()

    return '', 204

if __name__ == '__main__':
    app.run(port=5000)