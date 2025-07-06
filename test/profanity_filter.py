import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Use the environment variable securely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("Missing GEMINI_API_KEY in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-pro")

def clean_text(text: str) -> str:
    prompt = (
        "Check this script for any inappropriate content including swear words, slurs, or offensive phrases. "
        "Censor anything problematic using asterisks (****), but do not change the rest of the text:\n\n"
        f"{text}"
    )
    response = model.generate_content(prompt)
    return response.text.strip()
