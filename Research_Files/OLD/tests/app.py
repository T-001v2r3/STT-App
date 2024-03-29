from flask import Flask, request
#from flask_cors import CORS
#CORS(app)
from datetime import datetime
from google.cloud import speech
import os
import logging

# Set up logging
logging.basicConfig(filename='log.txt', level=logging.INFO, 
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def log_action(action):
    logging.info(action)

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    # audio fecthed from browser
    audio_file = request.files['audio']

    # current date and time
    now = datetime.now()
    # name files audio_Y_M_D_h_m_s.ogg
    filename = 'audio_{}.ogg'.format(now.strftime('%Y_%m_%d_%H_%M_%S'))

    # verify if file already exists, if true rename
    i = 1
    while os.path.exists(filename):
        name, ext = os.path.splitext(filename)
        filename = '{}_{}{}'.format(name, i, ext)
        i += 1

    audio_file.save(filename)

    # create a log file with client id's if possible
    log_action('Saved file: {}'.format(filename))
    # save on db the log for each alert

    client = speech.SpeechClient()

    with open(filename, 'rb') as audio_file:
        audio = speech.RecognitionAudio(content=audio_file.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        # this needs to be a config param from client
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    ## Process the response...
    for result in response.results:
        print(result.alternatives[0].transcript)

    # save on db path for the audio data

    return '', 204

if __name__ == '__main__':
    app.run(port=5000)
