# Desciption:
- We are bundling up everything at the Latest folder.
- the app must be running in order for the html be accessed properly.

# In progress:
- debuging the combined app:
	- currently fixing a new auth model.

# To do:
- Need to move credentials and url's to the env file.

# Temporary links:
- Root: https://34.134.1.128/
- App: https://34.134.1.128/STT-App/

# OLD folder:
These scripts are the components we used for the bundled solution in the latest folder:

## app_v2.py
- BUG: not saving uploaded files on gcloud, localhost works fine.
- The app recives the audio and saves it for further processing.
- There are two ways to feed the audio, file upload and direct record through the browser.
- First run 'python3 app.py' and then open 'index.html'.
- The app includes logs to a file.
- The app creates the entry on the db.
- This is a WIP.

## db_installer.py
- will only work from whitelisted ip adresses.
- connects to the gcloud db on the cloud and creates the db.
- there is a --clean flag to reset the db.
- This is a WIP.

## manual_file_to_speech_service.py
- reads from a file and asks for gcloud speech to text service.
- bad encoding for the file fetched from the browser? - ipython result:
	- InvalidArgument: 400 Invalid recognition 'config': bad encoding..
	- maybe this output can be prevented with a flag? check docs
- can't run outside ipython? 
- This is a WIP.

## lang_model.py
- uses a text generation model to parse the preprocessed text.
- saves ML resul on DB.
- This is a WIP.

# Basic instructions:
- must rename .env_sample to .env
- run db installer.py
- run app_v2.py
- submit audio files via the index.html
- text to speech is still manual for now

# Db Scheme:
- EntryID, maybe numbered auto incremented?
- Date and time of input;
- Audio file name;
- User Metadata, to identify the creator of this alert;
- Preprocessed plain text retrived from the audio (google stt results);
- Alert metadata, in here goes the ML model results;

# Dependencies (incomplete)
- pip install flask
- pip install python-dotenv
- pip install psycopg2
- pip install --upgrade google-cloud-speech
- pip install -U flask-cors
- pip install google-cloud-aiplatform
