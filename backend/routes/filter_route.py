"""
A route for handling filter-related operations in the backend.

- Profanity Filter using GEMINI

"""

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

from services import profanityfilter


# -------------------------------------------------------------------- #
# blueprint

filter_blueprint = Blueprint("filter", __name__)
api = Api(filter_blueprint)


# constants
profanityfilter.init_genai()
GEMINI_INSTANCE = profanityfilter.GeminiModel(profanityfilter.GEMINI_FLASH_2_5_MODEL)

# -------------------------------------------------------------------- #
# utils

def filter_clean_text(model: profanityfilter.GeminiModel, dirty_text: str):
    """
    Clean the text using the Gemini model to filter out profanity.

    :param model: Instance of GeminiModel
    :param dirty_text: Text that may contain profanity
    :return: Cleaned text
    """

    prompt = f"""
    Check this script for any inappropriate content including swear words, slurs, or offensive phrases.
    Censor anything problematic using asterisks (****), but do not change the rest of the text.
    Do not include any additional comments or explanations.

    For example, if the text contains the words: "fuck", censor it as "****".
    Additionally, the output should not contain any URLs, links, or references to external content.

    You should only return the cleaned text without any additional formatting or comments.
    The text begins now:
    {dirty_text}
"""

    response = model.send_prompt(prompt)
    return response.text.strip() if response.text.strip() else dirty_text, response.text.strip() is not None


# -------------------------------------------------------------------- #
# routes

@api.resource("/profanity", methods=["POST"])
class ProfanityFilter(Resource):
    def post(self):
        """
        Endpoint to filter profanity from a given text prompt.
        :return: JSON response with filtered text.

        :param: prompt = str
        """

        print(request.json)

        data = request.json
        if not data or "prompt" not in data:
            return jsonify({"error": "Invalid input, 'prompt' is required"}), 400

        # find dirty_text
        prompt = data["prompt"]

        # request cleaning
        cleaned_text, model_response = filter_clean_text(GEMINI_INSTANCE, prompt)
        
        print(f"Cleaned text: {cleaned_text}")
        print(f"Model response: {model_response}")

        # check if the model response is empty
        return {"cleaned_text": cleaned_text, "model_response": model_response}, 200
