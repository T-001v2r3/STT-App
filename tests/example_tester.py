config = speech.RecognitionConfig(
  language_code="pt",
  enable_automatic_punctuation=True,
  enable_word_time_offsets=True,
)

audio = speech.RecognitionAudio()
with open("../audio_manel.ogg", "rb") as audio_file:
    audio_data = audio_file.read()

audio.content = audio_data

response = speech_to_text(config, audio)
print_response(response)
