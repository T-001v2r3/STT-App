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

vertexai.init(project="ba-glass-hack24por-2011", location="europe-west9")
parameters = {
	"max_output_tokens": 256,
	"temperature": 0.2,
	"top_p": 0.95,
	"top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison")

def generate_summary_and_save_to_db(report, filename):
	print("Start generate summary and save to db")
	print(f"Report: {report}")
	print(f"Filename: {filename}")
	with open("prompt.txt", "r") as prompt_file:
		prompt = prompt_file.read()
	prompt += f" {report}\n output:"

	print("Before model prediction")
	print(f"Prompt: {prompt}")
	print(f"Parameters: {parameters}")
	response = model.predict(prompt, **parameters)
	print(f"Response from Model: {response.text}")
	try:
		response_json = response.text
		response_json = response_json.replace("```json", "").replace("```", "").strip()
		response_json = json.loads(response_json)
		answer = response_json["answer"]
		print(f"Answer: {answer}")
	except Exception as e:
		print(f"Error: {e}")
	# send reponse to db
	output_alertdata_to_db(filename, answer)

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

def start_speech_process(audio_data, filename):
	print("Start speech to text process")
	# Now you can use args.var to access the value of the argument
	config = speech.RecognitionConfig(
		#encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,    
		#sample_rate_hertz=16000,
		language_code="en",
		enable_automatic_punctuation=True,
		enable_word_time_offsets=True,
	)

	audio = speech.RecognitionAudio()
	#with open(filename, "rb") as audio_file:
	#	audio_data = audio_file.read()

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
# save the ml result in db
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
			UPDATE {} SET AlertMetadata = %s WHERE audiofilename = %s
		""").format(sql.Identifier(dbname)), (alert_metadata_json, filename))
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
		print(f"Filename: {filename}")
		print(f"Data: {data}")
		db_alertdata_write(conn, filename, data)
		print("Alert data written. Closing connection...")
		conn.close()

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
		user_metadata_json = json.dumps(user_metadata)
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

def get_filename():
    # current date and time
	now = datetime.now()
	# name with date and time so it acts like unique id for the file
	filename = 'audio_{}.flac'.format(now.strftime('%Y_%m_%d_%H_%M_%S'))
	# verify if file already exists, if true rename
	i = 1
	while os.path.exists(filename):
		name, ext = os.path.splitext(filename)
		filename = '{}_{}{}'.format(name, i, ext)
		i += 1
	return filename

client = storage.Client(project="ba-glass-hack24por-2011")
def upload(data, content_type, worker_number):
	filename = get_filename()
	bucket = client.bucket('ba-report-bucket')
	blob = bucket.blob(filename)
	blob.upload_from_string(data, content_type=content_type)
	create_db_entry(filename, datetime.now(), f"'worker_number': 65'{worker_number}'")
	print("send data to speech to text")
	audio_on_text = start_speech_process(data, filename)
	print("send data to generate summary")
	print(audio_on_text)
	generate_summary_and_save_to_db(audio_on_text, filename)

@app.route('/upload', methods=['POST'])
def upload_form():
	file = request.files['audio']
	print(request.files)
	worker_number = request.form['worker_number']
	upload(file.read(), file.content_type, worker_number)
	return 'File uploaded successfully to Google Cloud Storage'

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
