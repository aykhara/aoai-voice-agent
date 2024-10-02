class SSMLGenerator:
    """
    Class to generate SSML (Speech Synthesis Markup Language) strings for speech synthesis.
    """

    def __init__(self):
        """
        Initialize the SSMLGenerator by loading the SSML template from a file.
        """
        with open('custom_ssml.xml', 'r') as file:
            self.ssml_template = file.read()

    def generate_ssml(self, text: str, speech_language: str, voice_name: str, rate: str) -> str:
        """
        Generate an SSML string by filling in the SSML template with the provided text, language, and voice settings.

        Args:
            text (str): The text to be synthesized.
            speech_language (str): The language of the speech.
            voice_name (str): The name of the voice to be used for synthesis.
            rate (str): The rate of speech.

        Returns:
            str: The generated SSML string.
        """
        return self.ssml_template.format(
            speech_language=speech_language,
            voice_name=voice_name,
            rate=rate,
            text=text
        )