# Description:
Docs in progress ...
It includes an ui to read previously added data and an ui to input audio:
- locahost:5001 to read
- localhost to write
both .py servers need to be running atm


# Contents:
- /latest/ Latest version, WIP directory
- /Research_Files/ Unorganized "backups", will be used for later clean up and document the project.

# Techinal info:
## Dependencies ( this may be incomplete):
- google cloud cli connected to an account properly configured
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

### /latest/ui/
- this contains the app frontend
### /latest/ui/index.html
- this is the ui to input the audio.
### /latest/ui/style.css
- a complement of index.html to improve interface design
### /latest/ui/main.js
- a complement of index.html to increase functionalities
### /latest/ui/imgs
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


SELECT * FROM "public"."new_database" LIMIT 1000;
DELETE FROM new_database;