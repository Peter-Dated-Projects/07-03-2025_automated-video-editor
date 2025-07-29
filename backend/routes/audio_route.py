"""
A route for handling audio-related operations in the backend.

- 

"""

from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource

from flask import current_app

from services import audio


# -------------------------------------------------------------------- #
# blueprint

audio_blueprint = Blueprint("audio", __name__)
api = Api(audio_blueprint)



# -------------------------------------------------------------------- #
# utils



# -------------------------------------------------------------------- #
# routes

@api.resource("/generate_segments", methods=["POST"])
class GenerateSegments(Resource):
    def post(self):
        """
        Endpoint to generate segments from audio files.
        :return: JSON response with the generated segments.
        """

        # check for data
        data = request.json
        if not data or "segments" not in data:
            return jsonify({"error": "No audio segments provided"}), 400

        # check for segments
        segments = data["segments"]
        if not isinstance(segments, list) or not segments:
            return jsonify({"error": "Invalid or empty segments list"}), 400

        # check for voice
        voice = data.get("voice", "bm_george")  # Default voice if not provided
        if voice not in audio.KOKORO_VOICES["british"]:
            return jsonify({"error": f"Invalid voice: {voice}"}), 400

        # begin processing
        print(f"Received {len(segments)} audio segments for processing.")
        results, duration = audio.generate_audio(
            pipeline=KOKORO_INSTANCE,
            segments=segments,
            voice=voice
        )
        print(results)

        # [ALPHA] CACHE - store in global flask cache
        current_app.config["EDITING_INSTANCE"]["segment_information"] = results
        current_app.config["EDITING_INSTANCE"]["duration"] = duration

        # return generate audio file information
        return {
            "message": "Transcripts generated successfully",
            "segments": segments,
            "results": results
        }, 200
