from google.cloud import speech

def speech_to_text(
    config: speech.RecognitionConfig,
    audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
    client = speech.SpeechClient()
    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)
    return response

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

def main():
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

if __name__ == "__main__":
    main()