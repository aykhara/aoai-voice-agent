import logging
import os

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

    def generate_response(self, intent: str, user_input: str) -> str:
        """
        Send the generated response text to OpenAI and get GPT response.

        Args:
            intent (str): The classified intent.
            user_input (str): The input text from the user.

        Returns:
            str: The generated GPT response.
        """

        if intent == self.intent_subcategory_1:
            prompt = self.prompt_subcategory_1
        elif intent == self.intent_subcategory_2:
            prompt = self.prompt_subcategory_2
        else:
            system_message_content = "I couldn't classify the intent."

        system_message = {
            "role": "system",
            "content": prompt
        }

        response = self.client.chat.completions.create(
            model=self.deployment_id,
            max_tokens=200,
            stream=True,
            messages=[
                system_message,
                {"role": "user", "content": user_input}
            ]
        )
        return response


    def ask_openai_streaming(self, prompt: str):
        """
        Stream responses from GPT-4o using OpenAI API.

        Args:
            prompt (str): The input text from the user.

        Yields:
            str: Streaming chunks of the generated response.
        """
        intent = self.classify_intent(prompt)
        logger.info(f"Classified intent: {intent}")
        response = self.generate_response(intent, prompt)

         # Yield each chunk as it's streamed
        for chunk in response:
            logger.info(f"Chunk received: {chunk}")
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta:
                    if hasattr(delta, 'content') and delta.content is not None:
                        logger.info(f"Streaming content received: {delta.content}")
                        yield delta.content
                    else:
                        logger.info(f"No content in this chunk. Delta: {delta}")
                else:
                    logger.warning(f"No delta found in choices. Choices: {chunk.choices}")
            else:
                logger.warning(f"No choices found in chunk. Chunk: {chunk}")