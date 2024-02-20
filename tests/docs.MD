# source
https://codelabs.developers.google.com/codelabs/cloud-speech-text-python3?hl=en#6

# SETUP:

gcloud auth list
config list project
gcloud config set project <PROJECT_ID>
gcloud services enable speech.googleapis.com
cd ~
virtualenv venv-speech
source venv-speech/bin/activate
pip install ipython google-cloud-speech
ipython



# AUDIO FORMATS
https://cloud.google.com/speech-to-text/docs/encoding
 
# WORD PROCESSOR
https://cloud.google.com/speech-to-text/docs/async-time-offsets

# Lang list
https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages

# Clean up

To clean up your development environment, from Cloud Shell:

    If you're still in your IPython session, go back to the shell: exit
    Stop using the Python virtual environment: deactivate
    Delete your virtual environment folder: cd ~ ; rm -rf ./venv-speech

To delete your Google Cloud project, from Cloud Shell:

    Retrieve your current project ID: PROJECT_ID=$(gcloud config get-value core/project)
    Make sure this is the project you want to delete: echo $PROJECT_ID
    Delete the project: gcloud projects delete $PROJECT_ID

Learn more

    Test the demo in your browser: https://cloud.google.com/speech-to-text
    Speech-to-Text documentation: https://cloud.google.com/speech-to-text/docs
    Python on Google Cloud: https://cloud.google.com/python
    Cloud Client Libraries for Python: https://github.com/googleapis/google-cloud-python
