import logging
import time

import azure.cognitiveservices.speech as speechsdk

from src.services.openai_service import OpenAIService
from src.services.speech_service import SpeechService
from src.utils.settings import settings

logger = logging.getLogger(__name__)

def setup_logging():
    """
    Set up logging for the application.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

def main() -> None:
    """
    Main function to run the speech-to-text and text-to-speech application.

    This function continuously listens for speech input, classifies the intent using OpenAI,
    generates a response based on the classified intent, and synthesizes the response back to speech.

    The function sets up logging, initializes the OpenAI and Speech services, and enters an infinite loop
    where it performs the following steps:
    1. Listens for speech input.
    2. Recognizes and processes the speech input.
    3. Classifies the intent of the recognized speech using OpenAI.
    4. Generates a response based on the classified intent.
    5. Synthesizes the generated response to speech and plays it back.

    The loop continues until the user says 'Stop' or an EOFError is encountered.

    Returns:
        None
    """
    setup_logging()
    logging.info("Starting the application")

    openai_service = OpenAIService(settings.OPEN_AI_ENDPOINT, settings.OPEN_AI_KEY, settings.OPEN_AI_DEPLOYMENT_NAME, settings.INTENT_SUBCATEGORY_1, settings.INTENT_SUBCATEGORY_2, settings.PROMPT_CLASSIFY_INTENT, settings.PROMPT_SUBCATEGORY_1, settings.PROMPT_SUBCATEGORY_2)
    speech_service = SpeechService(settings.SPEECH_KEY, settings.SPEECH_REGION, settings.SPEECH_LANGUAGE, settings.SPEECH_VOICE, settings.SPEECH_SEGMENT_SILENCE_TIMEOUT)

    while True:
        logger.info("Azure OpenAI is listening. Say 'Stop' or press Ctrl-Z to end the conversation.")
        try:
            start_time = None
            # Recognize speech input
            speech_recognition_result = speech_service.recognize_speech()

            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                if speech_recognition_result.text.lower() == "stop":
                    logger.info("Conversation ended.")
                    break
                logger.info("Recognized speech: %s", speech_recognition_result.text)

                start_time = time.time()

                # GPT response via OpenAI service (streaming)
                streaming_response = openai_service.ask_openai_streaming(speech_recognition_result.text)

                tts_start_time = time.time()
                latency = (tts_start_time - start_time) * 1000
                logger.info("Time from end of speech to response preparation and start of TTS: %d ms", latency)

                # Stream the response as it is being received and synthesize it to speech
                full_response = ""
                for chunk in streaming_response:
                    logger.info(f"Received chunk: {chunk}")
                    if chunk:
                        full_response += chunk
                        # Start streaming the speech synthesis as chunks come in
                        speech_service.synthesize_speech_streaming(chunk, settings.SPEECH_RATE)

                logger.info(f"Full response: {full_response}")

                # # Synthesize the GPT response and speak it out
                # result = speech_service.synthesize_speech(gpt_response, settings.SPEECH_RATE)
                # first_byte_latency = int(result.properties.get_property(speechsdk.PropertyId.SpeechServiceResponse_SynthesisFirstByteLatencyMs))
                # finished_latency = int(result.properties.get_property(speechsdk.PropertyId.SpeechServiceResponse_SynthesisFinishLatencyMs))
                # result_id = result.result_id
                # logger.info("First byte latency (TTS): %d ms", first_byte_latency)
                # logger.info("Finished latency (TTS): %d ms", finished_latency)
                # # logger.info("Result ID: %s", result_id)

            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                logger.info("No speech could be recognized.")
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                logger.info("Speech Recognition canceled: %s", cancellation_details.reason)
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logger.error("Error details: %s", cancellation_details.error_details)
        except EOFError:
            break
        except Exception as e:
            logger.error("An error occurred: %s", e)

if __name__ == "__main__":
    main()