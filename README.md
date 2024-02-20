# Temporary links:
- Root: https://34.134.1.128/
- App: https://34.134.1.128/STT-App/

# Current State:
- The app recives the audio and saves it for further processing.
- There are two ways to feed the audio, file upload and direct record through the browser.
- First run 'python3 app.py' and then open 'index.html'.
- The app includes logs.
- This is a WIP.

# To do:
- Add the db connection to create each alert entry for further processing.

# Db Scheme:
- EntryID, maybe numbered auto incremented?
- Date and time of input;
- Audio file name;
- User Metadata, to identify the creator of this alert;
- Preprocessed plain text retrived from the audio (google stt results);
- Alert metadata, in here goes the ML model results;
