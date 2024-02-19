config = speech.RecognitionConfig(
    language_code="fr",
	# language_code="en",
    enable_automatic_punctuation=True,
    enable_word_time_offsets=True,
)
audio = speech.RecognitionAudio(
  uri="gs://cloud-samples-data/speech/corbeau_renard.flac",
#    uri="gs://cloud-samples-data/speech/brooklyn_bridge.flac",
)

response = speech_to_text(config, audio)
print_response(response)

# fr
