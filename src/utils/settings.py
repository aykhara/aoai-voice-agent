import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Class to manage environment settings.
    Retrieves setting values from environment variables and provides them as properties.
    """

    def __init__(self):
        self.OPEN_AI_KEY = self.get_env_variable("OPEN_AI_KEY")
        self.OPEN_AI_ENDPOINT = self.get_env_variable("OPEN_AI_ENDPOINT")
        self.OPEN_AI_DEPLOYMENT_NAME = self.get_env_variable("OPEN_AI_DEPLOYMENT_NAME")
        self.SPEECH_KEY = self.get_env_variable("SPEECH_KEY")
        self.SPEECH_REGION = self.get_env_variable("SPEECH_REGION")
        self.SPEECH_LANGUAGE = self.get_env_variable("SPEECH_LANGUAGE")
        self.SPEECH_VOICE = self.get_env_variable("SPEECH_VOICE")
        self.SPEECH_RATE = self.get_env_variable("SPEECH_RATE")
        self.SPEECH_SEGMENT_SILENCE_TIMEOUT = self.get_env_variable("SPEECH_SEGMENT_SILENCE_TIMEOUT")
        self.INTENT_SUBCATEGORY_1 = self.get_env_variable("INTENT_SUBCATEGORY_1")
        self.INTENT_SUBCATEGORY_2 = self.get_env_variable("INTENT_SUBCATEGORY_2")
        self.PROMPT_CLASSIFY_INTENT = self.get_env_variable("PROMPT_CLASSIFY_INTENT")
        self.PROMPT_SUBCATEGORY_1 = self.get_env_variable("PROMPT_SUBCATEGORY_1")
        self.PROMPT_SUBCATEGORY_2 = self.get_env_variable("PROMPT_SUBCATEGORY_2")

    def get_env_variable(self, var_name):
        """
        Retrieves the value from the specified environment variable name, and raises an error if it is not set.

        Parameters:
        - var_name (str): The name of the environment variable to retrieve.

        Returns:
        - str: The value of the environment variable.

        Raises:
        - RuntimeError: If the environment variable is not set.
        """
        value = os.getenv(var_name)
        if value is None:
            raise RuntimeError(f"Missing required environment variable: {var_name}")
        return value

# Create a settings instance as a singleton
settings = Settings()
