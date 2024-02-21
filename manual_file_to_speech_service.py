from google.cloud import speech

import argparse
# db stuff
import os
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_service_key.json'

# save the data on the preprocessedtext table
def db_preprocessedtext_write(conn, dbname, filename, data):
    print("Start preprocessed text added to the table")
    try:
        cur = conn.cursor()
        if dbname is None:
            print("DB_NAME environment variable is not set")
            return
        # Convert the user_metadata set to a list and then to a JSON string
        preprocessedtext_metadata_json = json.dumps(list(data))
        cur.execute(sql.SQL("""
            UPDATE {} 
            SET PreprocessedText = %s
            WHERE audiofilename = %s
        """).format(sql.Identifier(dbname)), (preprocessedtext_metadata_json, filename))
    except Exception as e:
        print("Error executing SQL query: ", e)
        return
    try:
        conn.commit()
    except Exception as e:
        print("Error committing transaction: ", e)
        return
    print("Completed, preprocessed text added to the table.")

def output_to_db(filename, data):
    db_credentials = {
        'host':    '34.163.172.208',
        'port':    '5432',
        'user':    'postgres',
        'password':'12345',
        'dbname':  'new_database'
    }
    print("DB host: ", db_credentials['host'])
    print("DB port: ", db_credentials['port'])
    print("DB user: ", db_credentials['user'])
    print("DB pass: ", db_credentials['password'])
    print("DB name: ", db_credentials['dbname'])

    print("Attempting to connect to the database...")
    conn = psycopg2.connect(**db_credentials)
    if conn:
        print("Connected to the new database. Attempting to write preprocessed text...")
        print("conn: ", conn)
        print("filename: ", filename)
        db_preprocessedtext_write(conn, db_credentials['dbname'], filename, data)
        print("preprocessed text written. Closing connection...")
        conn.close()

def speech_to_text(
    config: speech.RecognitionConfig,
    audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
    client = speech.SpeechClient()
    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)
    return response

def print_response(response: speech.RecognizeResponse):
    for result in response.results:
        print_result(result)

def print_result(result: speech.SpeechRecognitionResult):
    best_alternative = result.alternatives[0]
    print("-" * 80)
    print(f"language_code: {result.language_code}")
    print(f"transcript:    {best_alternative.transcript}")
    print(f"confidence:    {best_alternative.confidence:.0%}")
    print("-" * 80)
    for word in best_alternative.words:
        start_s = word.start_time.total_seconds()
        end_s = word.end_time.total_seconds()
        print(f"{start_s:>7.3f} | {end_s:>7.3f} | {word.word}")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--var', help='Description of the argument')
    args = parser.parse_args()

    # Now you can use args.var to access the value of the argument
    print(args.var)
    config = speech.RecognitionConfig(
        #encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,    
        #sample_rate_hertz=16000,
        language_code="en",
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True,
    )
    # filename = "audio_2024_02_21_12_23_16.webm"
    filename = args.var

    audio = speech.RecognitionAudio()
    with open(filename, "rb") as audio_file:
        audio_data = audio_file.read()

    audio.content = audio_data
    print("ola")
    print("ola")

    response = speech_to_text(config, audio)
    print("ola")
    print("ola")
    print("response: ", response)
    print_response(response)

    # send reponse to db
    output_to_db(filename, data = [result.alternatives[0].transcript for result in response.results])

if __name__ == "__main__":
    main()
