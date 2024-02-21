import unittest
from unittest.mock import patch, MagicMock
from google.cloud import speech

class TestSpeechToText(unittest.TestCase):
    @patch('google.cloud.speech.SpeechClient')
    def test_speech_to_text(self, mock_speech_client):
        # Arrange
        mock_speech_client().recognize.return_value = MagicMock()

        config = speech.RecognitionConfig(
            language_code="fr",
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
        )
        audio = speech.RecognitionAudio(
            uri="gs://cloud-samples-data/speech/corbeau_renard.flac",
        )

        # Act
        response = speech_to_text(config, audio)

        # Assert
        mock_speech_client().recognize.assert_called_once_with(config=config, audio=audio)
        self.assertIsInstance(response, MagicMock)

if __name__ == '__main__':
    unittest.main()
