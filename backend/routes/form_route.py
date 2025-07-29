"""
A route for handling audio-related operations in the backend.

- 

"""

import shutil
import os
from flask import Blueprint, jsonify, request, url_for, current_app
from flask_restful import Api, Resource

from services import audio, redditscraper, generator

import numpy as np


# for video + audio processing
import moviepy

import numpy as np


# -------------------------------------------------------------------- #
# blueprint

form_blueprint = Blueprint("form", __name__)
api = Api(form_blueprint)

# constants
AUDIO_GENERATED_FOLDER = "static/audio/generated"
TARGET_VIDEO_LOCATION = "static/video/result.mp4"
TARGET_STATIC_VIDEO_LOCATION = "video/result.mp4"
TARGET_CONCAT_AUDIO_FILE = "static/audio/generated/concat_audio.wav"
REQUIRED_FIELDS = [
    "source_url", "width", "height", "audio_voice", "audio_language", "video_title", 
    "video_description", "intro_image", "background_video"
]

# instances
REDDIT_SCRAPER_INSTANCE = redditscraper.RedditScraperBot(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# -------------------------------------------------------------------- #
# utils

def validate_form_data(data):
    """
    Validate the form data to ensure required fields are present.

    :param data: Dictionary containing form data
    :return: True if valid, raises ValueError if invalid
    """
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            raise ValueError(f"Missing required field: {field}")
    return True


# -------------------------------------------------------------------- #
# routes


@api.resource("/generate", methods=["POST"])
class FormSubmit(Resource):
    def post(self):
        """
        Handle form submission. Expects JSON body with required fields.
        
        :return: JSON response indicating success or failure
        """
        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400
        try:
            validate_form_data(data)
        except ValueError as e:
            print(f"Validation error: {e}")
            return {"error": str(e)}, 400


        # -------------------------------------------------------------------- #
        # [ALPHA] Debug -- the data received
        print("Received form data:", data)

        # create variables
        form_source_url = data.get("source_url")
        form_width = int(data.get("width", 1080))
        form_height = int(data.get("height", 1920))
        form_audio_voice = data.get("audio_voice", "bm_george")
        form_audio_language = audio.KOKORO_LANGUAGES[data.get("audio_language", "british")]
        form_video_title = data.get("video_title", "My Video")
        form_video_description = data.get("video_description", "This is a test video description.")
        form_intro_image = data.get("intro_image", False)
        form_background_video = data.get("background_video", None)
        form_text_time_padding = float(data.get("text_time_padding", 0))
        form_framerate = float(data.get("framerate", 30))

        # store form settings in Flask config
        def format_number(val):
            if isinstance(val, float) and val.is_integer():
                return str(int(val))
            return str(val)

        current_app.config["EDITING_INSTANCE"]["form"] = {
            "source_url": form_source_url,
            "width": format_number(form_width),
            "height": format_number(form_height),
            "audio_voice": form_audio_voice,
            "audio_language": audio.KOKORO_LANGUAGE_INVERSE[form_audio_language],
            "video_title": form_video_title,
            "video_description": form_video_description,
            "intro_image": form_intro_image,
            "background_video": form_background_video,
            "text_time_padding": format_number(form_text_time_padding),
            "framerate": format_number(form_framerate)
        }

        # create directories
        os.makedirs(AUDIO_GENERATED_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(TARGET_VIDEO_LOCATION), exist_ok=True)

        # scrape reddit for text
        _reddit_info = REDDIT_SCRAPER_INSTANCE.extract_post_details_url(form_source_url)
        if not _reddit_info:
            return {"error": "Failed to extract content from Reddit post"}, 400

        # create kokoro instance
        _kokoro_pipeline = audio.create_kokoro_pipeline(form_audio_language)
        if not _kokoro_pipeline:
            return {"error": "Failed to create Kokoro pipeline"}, 500
        
        # create video generator
        _video_generator = generator.BrainrotClipGenerator(
            video_text=_reddit_info["selftext"],
            video_file=form_background_video,
            kokoro_model=_kokoro_pipeline,
            debug_output=True,                  # [ALPHA] Debug output
            framerate=form_framerate,
            inter_segment_delay=form_text_time_padding,
        )

        # split text into segments
        _video_generator.split_text_into_segments(
            max_words=10,
            max_chars=1e9,
        )

        # define functions
        def text_clip_modifier(text_settings: dict, text: str, segment_index: int) -> dict:
            # check length of words
            _word_count = len(text.split())
            if _word_count > 10:
                text_settings["font_size"] = 80 - 20 * min(1, _word_count / 20)

            # set width + height
            text_settings["width"] = form_width * 0.8
            text_settings["height"] = form_height * 0.2
            return text_settings

        def bounce_pop(t):
            if t < 0.1:
                # Quick initial growth
                return 0.98 + 2 * t  # 0.98 to 1.0 in first 0.1s
            elif t < 0.3:
                # Overshoot and bounce
                return 1.0 + 0.05 * np.sin(3.14 / 0.2 * (t - 0.1))
            else:
                # Settle to final size
                return 1.0

        def modifier_func(segment: dict) -> dict:
            """
            Modify the text clip in the segment to apply a bounce pop effect.
            """
            segment["text_clip"] = segment["text_clip"].resized(bounce_pop)
            return segment

        # generate audio segments
        _segment_information = _video_generator.generate_segments(   
            AUDIO_GENERATED_FOLDER,
            form_audio_voice,
        )
        print(_segment_information)
        # modify segment information to store url object instead of strings
        for i, segment in _segment_information.items():
            # remove static/ from start of filename
            fname = segment["file"].replace("static/", "")
            # generate full URL for audio file
            segment["audio_url"] = url_for('static', filename=fname, _external=True)
        current_app.config["EDITING_INSTANCE"]["segment_information"] = _segment_information

        # apply effects to text clips
        _video_generator.apply_text_effect(modifier_func)

        # --- concat all audio segments into 1 file
        _video_generator.concat_audio_segment_files(TARGET_CONCAT_AUDIO_FILE)

        # extract only up until the audio length
        # and reduce framerate to 24fps
        moviepy.config.FFMPEG_BINARY = "ffmpeg"
        moviepy.config.IMAGEMAGICK_BINARY = "magick"

        # setup editor
        _video_generator.setup()
        _video_generator.composite_clips()

        # render the final video
        _video_generator.render(TARGET_VIDEO_LOCATION)
        _video_generator.cleanup(delete_files=False)

        # return success response
        print("Video generated successfully.")

        return {"message": "Form submitted successfully", "data": data, "post": _reddit_info}, 200



@api.resource("/result_url", methods=["GET"])
class ResultURL(Resource):
    def get(self):
        """
        Get the URL of the generated video result.
        """

        if not os.path.exists(TARGET_VIDEO_LOCATION):
            return {"error": "Video file not found"}, 404

        # [ALPHA] Debug output
        print(f"Video file exists at: {TARGET_VIDEO_LOCATION}")

        return {"result_url": url_for('static', filename=TARGET_VIDEO_LOCATION, _external=True)}, 200


@api.resource("/audio_segments", methods=["GET"])
class AudioSegments(Resource):
    def get(self):
        """
        Get the list of generated audio segments.
        """
        audio_files = [f for f in os.listdir(AUDIO_GENERATED_FOLDER) if f.endswith('.wav')]
        if not audio_files:
            return {"error": "No audio segments found"}, 404

        audio_segments = []
        for file in audio_files:
            file_path = os.path.join(AUDIO_GENERATED_FOLDER, file)
            audio_segments.append({
                "file_name": file,
                "file_path": url_for('static', filename=f"assets/audio/generated/{file}", _external=True),
                "duration": audio.get_audio_duration(file_path),
            })

        return {"audio_segments": audio_segments}, 200

@api.resource("/get_current_project", methods=["GET"])
class GetCurrentProject(Resource):
    def get(self):
        """
        Get the current project details.
        """
        # check if target video file exists
        if not os.path.exists(TARGET_VIDEO_LOCATION):
            return {"error": "Project not found"}, 203
        
        # check if audio segments exist
        audio_segments = [f for f in os.listdir(AUDIO_GENERATED_FOLDER) if f.endswith('.wav')]
        if not audio_segments:
            return {"error": "No audio segments found"}, 203

        print(current_app.config["EDITING_INSTANCE"]["segment_information"])

        segment_information = current_app.config["EDITING_INSTANCE"]["segment_information"].copy()
        # remove the video clip from segment information
        for segment in segment_information.values():
            segment.pop("text_clip", None)

        return {
            "result_url": url_for('static', filename=TARGET_STATIC_VIDEO_LOCATION, _external=True),
            "form_data": current_app.config["EDITING_INSTANCE"]["form"],
            "segment_information": segment_information,
        }, 200