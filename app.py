from flask import Flask, request
from google.cloud import speech
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    audio_file = request.files['audio']
    audio_file.save('audio.ogg')

    client = speech.SpeechClient()

    with open('audio.ogg', 'rb') as audio_file:
        audio = speech.RecognitionAudio(content=audio_file.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Process the response...
    for result in response.results:
        print(result.alternatives[0].transcript)
    # ...

    return '', 204

if __name__ == '__main__':
    app.run(port=5000)
