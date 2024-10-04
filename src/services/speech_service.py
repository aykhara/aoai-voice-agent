import logging
import os
import time

import azure.cognitiveservices.speech as speechsdk

from src.utils.ssml_generator import SSMLGenerator

logger = logging.getLogger(__name__)

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
        # silence_timeout = speech_segment_silence_timeout
        self.speech_config.set_property(speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, speech_segment_silence_timeout)
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
        # return self.speech_recognizer.recognize_once_async().get()
        recognition_start_time = time.time()
        result = self.speech_recognizer.recognize_once_async().get()
        recognition_end_time = time.time()

        recognition_latency = (recognition_end_time - recognition_start_time) * 1000
        logger.info(f"Speech recognition latency (STT): {recognition_latency} ms")

        return result

    def synthesize_speech_streaming(self, text: str, speech_rate: float):
        """
        Synthesize speech from the given text and stream audio data.

        Args:
            text (str): The text to be synthesized into speech.
            speech_rate (float): The rate at which the speech should be synthesized.

        Returns:
            None
        """
        ssml = self.ssml_generator.generate_ssml(
            text=text,
            speech_language=self.speech_config.speech_recognition_language,
            voice_name=self.speech_config.speech_synthesis_voice_name,
            rate=speech_rate
        )
        result = self.speech_synthesizer.speak_ssml_async(ssml).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioStarted:
            logger.info("Speech synthesis started.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech synthesis canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}")
            return

        # Stream the audio data while it's being synthesized
        audio_stream = speechsdk.AudioDataStream(result)
        audio_buffer = bytes(16000)
        filled_size = audio_stream.read_data(audio_buffer)
        while filled_size > 0:
            # Process and play the audio buffer here
            logger.info(f"{filled_size} bytes received and being played.")
            # Here you would typically send the audio buffer to be played in chunks
            filled_size = audio_stream.read_data(audio_buffer)