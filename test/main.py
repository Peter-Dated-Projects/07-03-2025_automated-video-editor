# change cwd to base directory of repo
import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
os.chdir(root_dir)
print("Working in directory:", os.getcwd())

# load up dotenv variables
from dotenv import load_dotenv
load_dotenv()

# for video + audio processing
import moviepy
from moviepy import VideoFileClip, TextClip, AudioFileClip, CompositeVideoClip

# for text to speech
from kokoro import KPipeline
import soundfile as sf

import torch
import numpy as np
import warnings
import datetime

from profanity_filter import clean_text

# suppress specific PyTorch warnings
warnings.filterwarnings("ignore", message="dropout option adds dropout after all but last recurrent layer")
warnings.filterwarnings("ignore", message="torch.nn.utils.weight_norm` is deprecated")

# local imports
from source.globals import (
    TARGET_VIDEO_WIDTH,
    TARGET_VIDEO_HEIGHT,
    SOURCE_FONT_FILE,
    TARGET_OUTPUT_FILE,
    TARGET_SEGMENTS_FOLDER,
    TARGET_SEGMENTS_CONCAT_FILE,
    TARGET_FRAMERATE,
    SOURCE_BACKGROUND_CLIP,
)
from source.generator import BrainrotClipGenerator
from source.redditscraper import RedditScraperBot

# detect available backend
if torch.cuda.is_available():
    DEVICE = "cuda"
    print("Using CUDA (GPU) backend for Torch.")
else:
    DEVICE = "cpu"
    print("Using CPU backend for Torch.")

# utility function to open file
def open_file_as(filepath, mode="r", encoding="utf-8"):
    with open(filepath, mode, encoding=encoding) as f:
        return f.read()

# fetch and clean script text
try:
    raw_script = open_file_as("assets/script.text")
    script = clean_text(raw_script)
except Exception as e:
    print(f"Warning: Profanity filter failed. Using raw script. Reason: {e}")
    script = open_file_as("assets/script.text")

# voice/language setup
SIMULATION_VOICE = BrainrotClipGenerator.KOKORO_VOICES["british"][0]
SIMULATION_LANGUAGE = BrainrotClipGenerator.KOKORO_LANGUAGES["british"]

# create kokoro instance
kokoro_pipeline = KPipeline(lang_code=SIMULATION_LANGUAGE, device=DEVICE)

# manual override flag
USE_MANUAL_TEXT = False

# main execution block
if __name__ == "__main__":
    # create reddit scraper instance
    reddit_scraper = RedditScraperBot()

    # fetch posts
    SUBREDDIT_NAME = "AITAH"
    top_posts = reddit_scraper.get_top_subreddit_posts(SUBREDDIT_NAME, limit=10)
    print(f"Fetched {len(top_posts)} posts from {SUBREDDIT_NAME} subreddit.")
    the_chosen_one = top_posts[0]
    print(f"Chosen post: {the_chosen_one.title}")

    # post details/media
    post_details = reddit_scraper.extract_post_details(the_chosen_one)
    print("Post details:", post_details)
    post_media = reddit_scraper.extract_post_media(the_chosen_one)
    if post_media:
        print("Post has media:", post_media)
    else:
        print("Post has no media.")

    # extract and clean post content
    post_content = the_chosen_one.selftext
    if not post_content:
        print("Post has no content. Exiting instead.")
        sys.exit(0)

    # run profanity filter
    try:
        SIMULATION_TEXT = clean_text(post_content)
        if SIMULATION_TEXT != post_content:
            os.makedirs("logs", exist_ok=True)
            with open("logs/filter_debug.txt", "a", encoding="utf-8") as f:
                f.write(f"--- {datetime.datetime.now()} ---\n")
                f.write("Original:\n" + post_content + "\n\n")
                f.write("Filtered:\n" + SIMULATION_TEXT + "\n\n")
    except Exception as e:
        print(f"Profanity filtering Reddit post failed: {e}")
        SIMULATION_TEXT = post_content

    # optional override
    if USE_MANUAL_TEXT:
        SIMULATION_TEXT = """
        This is a test text for the BrainrotClipGenerator.
        I just have to say Ethan is kinda dumb.
        Andrew is amazing and hot and beautiful!!
        I love this man.
        """

    print("Final simulation text:\n", SIMULATION_TEXT)

    # create generator instance
    video_generator = BrainrotClipGenerator(
        video_text=SIMULATION_TEXT,
        video_file=SOURCE_BACKGROUND_CLIP,
        kokoro_model=kokoro_pipeline,
        debug_output=True,
        framerate=TARGET_FRAMERATE,
        inter_segment_delay=0.1,
    )

    # segment setup
    video_generator.split_text_into_segments(
        max_words=10,
        max_chars=1e9,
    )

    # optional text size modifier
    def text_clip_modifier(text_settings: dict, text: str, segment_index: int) -> dict:
        _word_count = len(text.split())
        if _word_count > 10:
            text_settings["font_size"] = 80 - 20 * min(1, _word_count / 20)
        text_settings["width"] = TARGET_VIDEO_WIDTH * 0.8
        text_settings["height"] = TARGET_VIDEO_HEIGHT * 0.2
        return text_settings

    # generate TTS + visuals
    video_generator.generate_segments(
        TARGET_SEGMENTS_FOLDER,
        SIMULATION_VOICE,
    )

    # bounce pop animation
    def bounce_pop(t):
        if t < 0.1:
            return 0.98 + 2 * t
        elif t < 0.3:
            return 1.0 + 0.05 * np.sin(3.14 / 0.2 * (t - 0.1))
        else:
            return 1.0

    def modifier_func(segment: dict) -> dict:
        segment["text_clip"] = segment["text_clip"].resized(bounce_pop)
        return segment

    video_generator.apply_text_effect(modifier_func)

    # merge audio
    video_generator.concat_audio_segment_files(TARGET_SEGMENTS_CONCAT_FILE)

    # moviepy config
    moviepy.config.FFMPEG_BINARY = "ffmpeg"
    moviepy.config.IMAGEMAGICK_BINARY = "magick"

    # compose and render
    video_generator.setup()
    video_generator.composite_clips()
    video_generator.render(TARGET_OUTPUT_FILE)
    video_generator.cleanup()
