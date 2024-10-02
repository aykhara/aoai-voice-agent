import os

import azure.cognitiveservices.speech as speechsdk

from src.utils.ssml_generator import SSMLGenerator


class SpeechService:
    """
    Service class to handle speech recognition and synthesis using Azure Cognitive Services.
    """

    def __init__(self, speech_key: str, speech_region: str, speech_language: str, speech_voice: str, speech_segment_silence_timeout: int):
        """
        Initialize the SpeechService with environment variables and set up the speech configuration.

        Parameters:
            speech_key (str): The API key for the speech service.
            speech_region (str): The region where the speech service is hosted.
            speech_language (str): The language to be used by the speech service.
            speech_voice (str): The voice to be used by the speech service.
            speech_segment_silence_timeout (int): The timeout duration for speech segment silence in milliseconds.
        """
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region,
        )
        self.speech_config.speech_recognition_language = speech_language
        self.speech_config.speech_synthesis_voice_name = speech_voice
        silence_timeout = speech_segment_silence_timeout
        self.speech_config.set_property(speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, silence_timeout)
        self.audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config
        )
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=self.audio_output_config
        )
        self.tts_sentence_end = [ ".", "!", "?", ";", "。", "！", "？", "；", "\n" ]
        self.ssml_generator = SSMLGenerator()

    def recognize_speech(self) -> speechsdk.SpeechRecognitionResult:
        """
        Recognize speech from microphone input.

        Returns:
            speechsdk.SpeechRecognitionResult: The result of the speech recognition.
        """
        return self.speech_recognizer.recognize_once_async().get()

    def synthesize_speech(self, text: str, speech_rate: float) -> speechsdk.SpeechSynthesisResult:
        """
        Synthesize text to speech using SSML template.

        Args:
            text (str): The text to be synthesized.

        Returns:
            speechsdk.SpeechSynthesisResult: The result of the speech synthesis.
        """
        ssml = self.ssml_generator.generate_ssml(
            text=text,
            speech_language=self.speech_config.speech_recognition_language,
            voice_name=self.speech_config.speech_synthesis_voice_name,
            rate=speech_rate
        )
        return self.speech_synthesizer.speak_ssml_async(ssml).get()