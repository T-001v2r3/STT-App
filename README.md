# Context:
This project was developed during BA Glass Creative Labs event suported by Google.
This project is work in progress.

# Description:
Docs in progress ...
It includes an ui to read previously added data and an ui to input audio, as well a webserver for each interface.

# Usage:
Follow the steps in the right order:
- install gcloud cli and authenticate
- verify .env credentials
- verify google cloud bucket credentials
- run /latest/ui/read_data/app.py to start the app that enables read access to incident logs
- access locahost:5001 to read incident logs
- run /latest/app/main.py installdb to create the database, table and rows.
- (optional) run /latest/app/main.py resetdb if you want to clean the db
- run /latest/app/main.py to start the app
that deals with the input interface
- open /latest/ui/input_data/index.html to input an audio with a new incident

# Contents:
- /latest/ Latest version, WIP directory
- /Research_Files/ Unorganized "backups", will be used for later clean up and document the project.

# Techinal info:
## Dependencies ( this may be incomplete):
- google cloud cli connected to an account properly configured
- a postgres database server
- a google cloud bucket
- pip install flask
- pip install python-dotenv
- pip install psycopg2
- pip install --upgrade google-cloud-speech
- pip install -U flask-cors
- pip install google-cloud-aiplatform

## Folder scheme:
### /Research_Files/:
This folder is going to be claened up later.
These are the components used to build the final.
They were made under a research context so they aren't accurate compared to the final solution.
They all work standalone under specific circuntances.

### /Research_Files/app_v2.py
- BUG: not saving uploaded files on gcloud, localhost works fine.
- The app recives the audio and saves it for further processing.
- There are two ways to feed the audio, file upload and direct record through the browser.
- First run 'python3 app.py' and then open 'index.html'.
- The app includes logs to a file.
- The app creates the entry on the db.
- This is a WIP.

### /Research_Files/db_installer.py
- will only work from whitelisted ip adresses.
- connects to the gcloud db on the cloud and creates the db.
- there is a --clean flag to reset the db.
- This is a WIP.

### /Research_Files/manual_file_to_speech_service.py
- reads from a file and asks for gcloud speech to text service.
- bad encoding for the file fetched from the browser? - ipython result:
	- InvalidArgument: 400 Invalid recognition 'config': bad encoding..
	- maybe this output can be prevented with a flag? check docs
- can't run outside ipython? 
- This is a WIP.

### /Research_Files/lang_model.py
- uses a text generation model to parse the preprocessed text.
- saves ML resul on DB.
- This is a WIP.

### /latest/
- this includes the latest version of the work in progress files

### /latest/app/
- this contains the app backend
### /latest/app/application_default_credentials.json
- not sure if we need this at the moment
### /latest/app/main.py
- this program needs to be running.
### /latest/app/.env
- credentials file
### /latest/app/prompt.txt
- previous genrated examples to feed the model
- this content improves the quality of the output

### /latest/ui/input_data/
- the app to input audio
### /latest/ui/input_data/index.html
- this is the ui to input the audio.
### /latest/ui/input_data/style.css
- a complement of index.html to improve interface design
### /latest/ui/input_data/main.js
- a complement of index.html to increase functionalities
### /latest/ui/input_data/imgs
- images to feed the user interface

### /latest/ui/read_data/
- the app to display previously inputed data
### /latest/ui/read_data/app.py
- a webserver to retrieve db data
### /latest/ui/read_data/index.html
- user interfce to read previous incidents
### /latest/ui/read_data/static/imgs
- images to feed the user interface

### /latest/test_audio_files/
- audio examples for testing purposes
### /latest/test_audio_files/speech_brooklyn_bridge.flac
- english language audio file example (source: google documentation)

## Data Storage:
We use the database to store the information gathered in the whole process.

### Database Scheme:
- EntryID, unique auto incremented number
- Date and time of input;
- Audio file name;
- User Metadata, to identify the creator of this alert;
- Preprocessed plain text retrived from the audio (google stt results);
- Alert metadata, in here goes the ML model results;

### Goggle Cloud Buckets
- the place where the audio files get saved.

# TO DO:
- BUG! the response from ai gets saves an array with characters splited by arguments. nothing is lost, just needs to be tweaked. 
- a new logic for response parsing/storing/organizing/tabling was in planning but isnt proplerly allogned or coded yet. maybe using a new db table and split the possible reported parameters and use ai to analise the data and fill in other parameters that may be concluded from the analisis like severity possible recomendations or risks that that report may cause.
- There is a lot to do this is just some of it:
	- DELETE FROM database_name; needs to be done when the clean arg is passed;
	- need to see why not creating db when insatll arg is passed;
	- Need to move credentials and url's to the env file.
	- make a config file
	- add a language parameter on the ui and use it from there
 - create a link between read and impit pages
 - rework ui's so everything stays in place when the window is rescaled
	- verify if we need the json credentials file
- get a download link for each audio and add it on db and get it displsyed
- combine .py servers

# Usefull db querries:
SELECT * FROM "public"."new_database" LIMIT 1000;
DELETE FROM new_database;