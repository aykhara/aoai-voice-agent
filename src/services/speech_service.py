import logging
import time

import azure.cognitiveservices.speech as speechsdk

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
        # SpeechConfig for STT
        self.speech_recognition_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        self.speech_recognition_config.speech_recognition_language = speech_language
        self.speech_recognition_config.set_property(
            speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs,
            speech_segment_silence_timeout
        )

        # SpeechConfig for TTS
        self.speech_synthesis_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            endpoint=f"wss://{speech_region}.tts.speech.microsoft.com/cognitiveservices/websocket/v2"
        )
        self.speech_synthesis_config.speech_synthesis_voice_name = speech_voice

        self.audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_recognition_config,
            audio_config=self.audio_config
        )
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_synthesis_config,
            audio_config=self.audio_output_config
        )

    def recognize_speech(self) -> speechsdk.SpeechRecognitionResult:
        """
        Recognize speech from microphone input.

        Returns:
            speechsdk.SpeechRecognitionResult: The result of the speech recognition.
        """
        logger.info("Starting speech recognition...")
        self.speech_recognizer.recognizing.connect(self._recognizing_handler)
        self.speech_recognizer.recognized.connect(self._recognized_handler)

        result = self.speech_recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info(f"Recognized: {result.text}")
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logger.info("No speech could be recognized.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(f"Error details: {cancellation_details.error_details}")

        return result

    def synthesize_speech(self, text: str) -> speechsdk.SpeechSynthesisResult:
        """
        Synthesize given text to speech and return the result.

        Args:
            text (str): The text to synthesize.

        Returns:
            speechsdk.SpeechSynthesisResult: The result of the speech synthesis.
        """
        result = self.speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info("Speech synthesis completed successfully.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech synthesis canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}")

        return result

    def synthesize_streamed_audio(self, text: str) -> None:
        """
        Synthesize audio from the given text and stream each audio chunk to the client.

        Args:
            text (str): The text to synthesize and stream.
        """
        result = self.speech_synthesizer.start_speaking_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_data_stream = speechsdk.AudioDataStream(result)
            audio_buffer = bytes(16000)
            filled_size = audio_data_stream.read_data(audio_buffer)
            while filled_size > 0:
                logger.info(f"{filled_size} bytes received and being sent to client.")
                filled_size = audio_data_stream.read_data(audio_buffer)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech synthesis canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}")

    def _recognizing_handler(self, event: speechsdk.SpeechRecognitionEventArgs):
        """
        Handler for the recognizing event, which is triggered when speech is being recognized.

        Args:
            event (speechsdk.SpeechRecognitionEventArgs): The event arguments containing recognition details.
        """
        if event.result.reason == speechsdk.ResultReason.RecognizingSpeech and len(event.result.text) > 0:
            logger.info("Recognizing speech: %s", event.result.text)
            logger.info("Offset in Ticks: %d", event.result.offset)
            logger.info("Duration in Ticks: %d", event.result.duration)

    def _recognized_handler(self, event: speechsdk.SpeechRecognitionEventArgs):
        """
        Handler for the recognized event, which is triggered when speech has been recognized.

        Args:
            event (speechsdk.SpeechRecognitionEventArgs): The event arguments containing recognition details.
        """
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech and len(event.result.text) > 0:
            logger.info("Final recognized speech: %s", event.result.text)
            logger.info("Offset in Ticks: %d", event.result.offset)
            logger.info("Duration in Ticks: %d", event.result.duration)