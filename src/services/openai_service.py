import logging
import os
import time

import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, azure_endpoint: str, api_key: str, deployment_id: str, intent_subcategory_1: str, intent_subcategory_2: str, prompt_classify_intent: str, prompt_subcategory_1: str, prompt_subcategory_2: str):
        """
        Initialize the Azure OpenAI service.

        Parameters:
            azure_endpoint (str): Endpoint URL for the Azure OpenAI service.
            api_key (str): API key for the Azure OpenAI service.
            deployment_id (str): The deployment ID for the Azure OpenAI model.
            intent_subcategory_1 (str): The first subcategory of the intent.
            intent_subcategory_2 (str): The second subcategory of the intent.
            prompt_classify_intent (str): The prompt used to classify the intent.
            prompt_subcategory_1 (str): The prompt used for the first subcategory.
            prompt_subcategory_2 (str): The prompt used for the second subcategory.
        """
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2023-05-15"
        )
        self.deployment_id = deployment_id
        self.intent_subcategory_1 = intent_subcategory_1
        self.intent_subcategory_2 = intent_subcategory_2
        self.prompt_classify_intent = prompt_classify_intent.format(
            intent_subcategory_1=self.intent_subcategory_1,
            intent_subcategory_2=self.intent_subcategory_2
        )
        self.prompt_subcategory_1 = prompt_subcategory_1
        self.prompt_subcategory_2 = prompt_subcategory_2

    def classify_intent(self, user_input: str) -> str:
        """
        Classify the user's intent based on the input text.

        Args:
            user_input (str): The input text from the user.

        Returns:
            str: The classified intent.
        """
        system_message = {
            "role": "system",
            "content": self.prompt_classify_intent
        }

        # Send user input and system message to OpenAI
        response = self.client.chat.completions.create(
            model=self.deployment_id,
            max_tokens=50,
            messages=[
                system_message,
                {"role": "user", "content": user_input}
            ]
        )
        classified_intent = response.choices[0].message.content.strip()
        return classified_intent

    def ask_openai(self, prompt: str, speech_service, speech_rate: float) -> None:
        """
        Classify intent and generate GPT response in a streaming fashion with latency measurements for each synthesis chunk.

        Args:
            prompt (str): The input text from the user.
            speech_service: Instance of SpeechService to handle speech synthesis.

        Returns:
            None: Synthesizes responses as they are received and logs latency.
        """
        intent = self.classify_intent(prompt)
        logger.info(f"Classified intent: {intent}")

        # Start generating response based on intent
        if intent == self.intent_subcategory_1:
            prompt = self.prompt_subcategory_1
        elif intent == self.intent_subcategory_2:
            prompt = self.prompt_subcategory_2
        else:
            logger.warning("Could not classify intent.")
            return

        response = self.client.chat.completions.create(
            model=self.deployment_id,
            max_tokens=200,
            stream=True,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": prompt}
            ]
        )

        collected_messages = []
        last_tts_request = None

        # Iterate through the response stream and synthesize each chunk
        for chunk in response:
            if len(chunk.choices) > 0:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    collected_messages.append(chunk_message)
                    if any(punct in chunk_message for punct in speech_service.tts_sentence_end):
                        full_message = ''.join(collected_messages).strip()
                        if full_message:
                            logger.info(f"Speech synthesized for: {full_message}")

                            # Measure latency before synthesizing speech
                            tts_start_time = time.time()

                            result = speech_service.synthesize_speech(full_message, speech_rate)
                            first_byte_latency = int(result.properties.get_property(speechsdk.PropertyId.SpeechServiceResponse_SynthesisFirstByteLatencyMs))
                            finished_latency = int(result.properties.get_property(speechsdk.PropertyId.SpeechServiceResponse_SynthesisFinishLatencyMs))
                            result_id = result.result_id

                            # Log the latencies for each synthesized chunk
                            logger.info("First byte latency: %d ms", first_byte_latency)
                            logger.info("Finished latency: %d ms", finished_latency)
                            logger.info("Result ID: %s", result_id)

                            # Calculate total latency
                            total_latency = (time.time() - tts_start_time) * 1000
                            logger.info("Total synthesis latency: %d ms", total_latency)

                            last_tts_request = result
                            collected_messages.clear()

        if last_tts_request:
            last_tts_request.get()
