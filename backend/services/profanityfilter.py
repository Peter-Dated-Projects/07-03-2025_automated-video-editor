import os
import google.generativeai as genai
from dotenv import load_dotenv

from typing import List, Union, Dict
import mimetypes


# -------------------------------------------------------------------- #

GEMINI_PRO_MODEL = "gemini-2.5-pro"  # Default model, can be changed if needed
GEMINI_FLASH_2_5_MODEL = "gemini-2.5-flash"  # Flash model for faster responses, if available
GEMINI_PRO_FLASH_MODEL = (
    "gemini-2.5-flash"  # Flash model for faster responses, if available
)


def init_genai():
    """
    Initialize the Gemini AI client with the provided API key.

    :param api_key: Your Gemini API key
    """
    if "GEMINI_API_KEY" not in os.environ:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


class GeminiModel:
    def __init__(self, model_name: str):
        self.model = genai.GenerativeModel(model_name)

    # -------------------------------------------------------------------- #

    def _prepare_file(self, file_path: str) -> Dict:
        """
        Prepare a file for sending to Gemini by determining mime type and reading binary data.

        :param file_path: Path to the file
        :return: Dictionary with mime_type and data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine mime type from file extension
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            # Default to binary if we can't determine the type
            mime_type = "application/octet-stream"

        # Read file as binary
        with open(file_path, "rb") as f:
            data = f.read()

        return {"mime_type": mime_type, "data": data}

    # -------------------------------------------------------------------- #

    def send_prompt(self, prompt: str, files: List[str] = None):
        """
        Send a prompt to the Gemini model with optional files.

        :param prompt: Text prompt to send
        :param files: List of file paths to include
        :return: Gemini model response
        """
        if not files:
            # Text-only prompt
            return self.model.generate_content(prompt)

        # Process files
        prepared_files = []
        for file_path in files:
            try:
                file_data = self._prepare_file(file_path)
                prepared_files.append(file_data)
            except Exception as e:
                print(f"Warning: Failed to process file {file_path}: {e}")

        # Send prompt with files
        return self.model.generate_content(prompt, files=prepared_files)


# -------------------------------------------------------------------- #
# custom functions


def clean_text(text: str) -> str:
    model = GeminiModel(GEMINI_PRO_MODEL)

    prompt = f"""
        Check this script for any inappropriate content including swear words, slurs, or offensive phrases.
        Censor anything problematic using asterisks (****), but do not change the rest of the text.
        Do not include any additional comments or explanations.

        For example, if the text contains the words: "fuck", censor it as "****".
        Additionally, the output should not contain any URLs, links, or references to external content.

        You should only return the cleaned text without any additional formatting or comments.
        The text begins now:
        {text}
"""
    response = model.send_prompt(prompt)
    return response.text.strip()


# -------------------------------------------------------------------- #

if __name__ == "__main__":

    # Load from .env file
    load_dotenv()

    init_genai()

    sample_text = """
    This is a test text for the BrainrotClipGenerator.
    I just have to say Ethan is kinda dumb.
    Andrew is amazing and hot and beautiful!!
    I love this man.
    """

    cleaned_text = clean_text(sample_text)
    print(cleaned_text)
