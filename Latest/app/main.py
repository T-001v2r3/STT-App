#!/usr/bin/env python3
import vertexai
from vertexai.language_models import TextGenerationModel
from google.cloud import speech, storage
from google.oauth2 import service_account
from google.auth.transport import requests
import google.auth
import google.auth.exceptions
import google.auth.transport.requests
import argparse
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
import os
import logging
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import json
import sys
from flask import jsonify
app = Flask(__name__)
CORS(app)
##################################################################
###################### Credentials ###############################
##################################################################

# load the environment variables
load_dotenv() 

# google credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'application_default_credentials.json'

##################################################################
###################### ML Processing #############################
##################################################################

# save the data on the alert table
def db_alertdata_write(conn, filename, data):
	print("Start alert data added to the table")
	try:
		cur = conn.cursor()
		dbname = os.getenv('DB_NAME')
		if dbname is None:
			print("DB_NAME environment variable is not set")
			return
		# Convert the user_metadata set to a list and then to a JSON string
		alert_metadata_json = json.dumps(list(data))
		cur.execute(sql.SQL("""
			INSERT INTO {} (AlertMetadata) WHERE filename = %s
			VALUES (%s)
		""").format(sql.Identifier(dbname)), (filename, alert_metadata_json))
	except Exception as e:
		print("Error executing SQL query: ", e)
		return
	try:
		conn.commit()
	except Exception as e:
		print("Error committing transaction: ", e)
		return
	print("Completed, alert data added to the table.")

def output_alertdata_to_db(filename, data):
	db_credentials = {
		'host': os.getenv('DB_HOST'),
		'port': os.getenv('DB_PORT'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASS'),
		'dbname': os.getenv('DB_NAME'),
	}
	print("Attempting to connect to the database...")
	conn = psycopg2.connect(**db_credentials)
	if conn:
		print("Connected to the new database. Attempting to write alert data...")
		db_alertdata_write(conn, filename, data)
		print("Alert data written. Closing connection...")
		conn.close()

vertexai.init(project="ba-glass-hack24por-2011", location="us-central1")
parameters = {
	"max_output_tokens": 256,
	"temperature": 0.2,
	"top_p": 0.95,
	"top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison@001")

def generate_summary_and_save_to_db(report, filename):
	response = model.predict(
	""""We have a report from people of the glass factory floor and we need to extract data in json format in the following order: time(24 format), type_of_incident, location, if appliable the solution of that problem, and the shift. The shift normally is a letter A,B,C,D. The location two letters that represent the factory, number of the oven, the line, the section and the concavity, that is a letter A B or C. The keys must be in english but the data remains in the original language of input. The solution type and the problem type must be a short description in the language of input. The data should be in present tense.


Provide a summary with about two sentences for the following article: Ocorreu um erro nas mangueiras de assentamento do AV538C e paramos a producao para corrigir
Summary: ```json
[
	{
		"\"Time\": \"Não disponível\","
		"\"type_of_incident\": \"erro mangueiras de assentamento\","
		"\"location\": \"AV538C\","
		"\"solution\": \"Interrupção da Produção para manutenção\","
		"\"shift\": \"Não disponível\""
	}
]


Provide a summary with about two sentences for the following article: o defletor da estacao av893 empancou e tivemos que parar a producao para lubrificar o defleto. ocorreu no turno C
Summary: ```json
[
  {
	"\"Time\": \"Não disponível\","
	"\"type_of_incident\": \"Encravamento do defletor da estação\","
	"\"location\": \"AV893\","
	"\"solution\": \"Interupção da produção para lubrificação do defletor\","
	"\"shift\": \"C\""
  }
]
```


Provide a summary with about two sentences for the following article: no av52 no setor 8 por falha do rebentar da bola na cavidade A e braco de marizas partido.
Summary: ```json
[
  {
	"\"Time\": \"Não disponível\","
	"\"type_of_incident\": \"Bola rebentada,  braço de marisa partido\","
	"\"location\": \"AV528A\","
	"\"solution\": \"Não disponível\","
	"\"shift\": \"Não disponível\""
  }
]
```


Provide a summary with about two sentences for the following article:  no setor av548 BTC com problemas de excesso de temperatura, fizemos a limpeza do circuito de água de arrefecimento para resolver. ocorreu no turno A
Summary: ```json
[
  {
	"\"Time\": \"Não disponível\","
	"\"type_of_incident\": \"Excesso de temperatura no BTC\","
	"\"location\": \"AV548\","
	"\"solution\": \"Limpeza do circuito de água de arrefecimento\","
	"\"shift\": \"A\""
  }
]
```


Provide a summary with about two sentences for the following article: no turno A na AV566A a gota estava torta entao procedemos ao centramento da gota.
Summary: ```json
[
  {
	"\"Time\": \"Não disponível\","
	"\"type_of_incident\": \"Gota Desalinhada\","
	"\"location\": \"AV566A\","
	"\"solution\": \"Centragem da gota\","
	"\"shift\": \"A\""
  }
]
```


Provide a summary with about two sentences for the following article: no av456A, puncao demasiado quente, paramos o setor para aumentar 5º no 
 arrefecimento de ventilação na punção 
Summary: ```json
[
  {
	"\"Time\": \"Não disponível\","
	"\"type_of_incident\": \"Punção demasiado quente\","
	"\"location\": \"AV456A\","
	"\"solution\": \"Aumentar 5ºC no arrefecimento de ventilação na punção\","
	"\"shift\": \"Não disponível\""
  }
]
```

Provide a summary with about two sentences for the following article: {report}
Summary:
""",
	**parameters
)
	print(f"Response from Model: {response.text}")
	# send reponse to db
	output_alertdata_to_db(filename, response.text)

##################################################################
###################### Speech to Text ############################
##################################################################
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

def start_speech_process(filename):
	# Now you can use args.var to access the value of the argument
	config = speech.RecognitionConfig(
		#encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,    
		#sample_rate_hertz=16000,
		language_code="en",
		enable_automatic_punctuation=True,
		enable_word_time_offsets=True,
	)

	audio = speech.RecognitionAudio()
	with open(filename, "rb") as audio_file:
		audio_data = audio_file.read()

	audio.content = audio_data

	response = speech_to_text(config, audio)
	print_response(response)

	# send reponse to db
	output_to_db(filename, data = [result.alternatives[0].transcript for result in response.results])
	processed_response = [result.alternatives[0].transcript for result in response.results]
	return processed_response

def speech_to_text(
	config: speech.RecognitionConfig,
	audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
	client = speech.SpeechClient()
	# Synchronous speech recognition request
	response = client.recognize(config=config, audio=audio)
	return response

##################################################################
###################### Log file ##################################
##################################################################

# Set up logging
logging.basicConfig(filename='log.txt', level=logging.INFO, 
					format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def log_action(action):
	logging.info(action)

##################################################################
########################## DB ####################################
##################################################################
	
######## Speech to text ########
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

	print("Attempting to connect to the database...")
	conn = psycopg2.connect(**db_credentials)
	if conn:
		print("Connected to the new database. Attempting to write preprocessed text...")
		db_preprocessedtext_write(conn, db_credentials['dbname'], filename, data)
		print("preprocessed text written. Closing connection...")
		conn.close()

######## First entry stuff ########
# This function will add to the table the new entry
def db_entry_add(conn, filename, timestamp, user_metadata):
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

# This function will start the connection to the db
def create_db_entry(filename, timestamp, user_metadata):
	db_credentials = {
		'host': os.getenv('DB_HOST'),
		'port': os.getenv('DB_PORT'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASS'),
		'dbname': os.getenv('DB_NAME'),
	}

	print("Attempting to connect to the database...")
	conn = psycopg2.connect(**db_credentials)
	if conn:
		print("Connected to the new database. Attempting to add entry...")
		db_entry_add(conn, filename, timestamp, user_metadata)
		print("Entry process completed. Closing connection...")
		conn.close()

##################################################################
#################### Web Interface ###############################
##################################################################

# recive the audio filname and the transcribe text
@app.route('/request-transcribe', methods=['POST'])
def request_transcribe():
	filename = request.get_json()
	print("data: ", filename)
	report = start_speech_process(filename)
	generate_summary_and_save_to_db(report, filename)

# This is for the client to recive a final name for the file
@app.route('/decide-filename', methods=['GET'])
def decide_filename():
	# current date and time
	now = datetime.now()
	# name with date and time so it acts like unique id for the file
	filename = 'audio_{}.flac'.format(now.strftime('%Y_%m_%d_%H_%M_%S'))
	print("filename")
	# verify if file already exists, if true rename
	i = 1
	while os.path.exists(filename):
		name, ext = os.path.splitext(filename)
		filename = '{}_{}{}'.format(name, i, ext)
		i += 1
	print("filename: ", filename)
	return {'filename': filename}, 200

# This is for the client to send the audio file to the server
@app.route('/upload', methods=['POST'])
def upload():
	# audio fetched from browser
	audio_file = request.files['audio']

	# request a file name
	filename = decide_filename()
	print("filename: ", filename)
	audio_file.save(filename)

	# create a log file with client id's if possible
	log_action('Saved file: {}'.format(filename))
	
	# save on db the log for each alert
	now = datetime.now()
	create_db_entry(filename, now, {1})

	return '', 204


##################################################################
############################# Install db #########################
##################################################################

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

def run_install(clean):
	db_credentials = {
		'host': os.getenv('DB_HOST'),
		'port': os.getenv('DB_PORT'),
		'user': os.getenv('DB_USER'),
		'password': os.getenv('DB_PASS'),
		'dbname': os.getenv('DB_NAME'),
	}
	dbname = os.getenv('DB_NAME')
	print("Attempting to connect to the PostgreSQL server...")
	conn = psycopg2.connect(**db_credentials)
	conn.autocommit = True
	if clean == 1:
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

##################################################################
############################# MAIN ###############################
##################################################################
def main():
	print("Available arguments: resetdb & installdb.\n Description: resetdb will delete the current database and create a new one. installdb will create a new database if it does not exist. If the database already exists, it will not be created. If no argument is provided, the server will start.")
	if len(sys.argv) > 1:
		argument = sys.argv[1]
		if argument == 'resetdb':
			# Reset the database logic here
			print("Resetting the database...")
			run_install(1)
		elif argument == 'installdb':
			# Install the database logic here
			print("Installing the database...")
			run_install(0)
		else:
			print("Invalid argument. Please use '', 'resetdb' or 'installdb'.")
	else:
		app.run(port=5000)

if __name__ == '__main__':
	main()
