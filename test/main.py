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

# ---------------------------------------------------------------- #

# for video + audio processing
import moviepy
from moviepy import (
    VideoFileClip,
    TextClip,
    AudioFileClip,
    CompositeVideoClip,
)

# for text to speech
from kokoro import KPipeline
import soundfile as sf

import torch
import numpy as np
import warnings

import datetime

# Filter out specific PyTorch warnings
warnings.filterwarnings(
    "ignore", message="dropout option adds dropout after all but last recurrent layer"
)
warnings.filterwarnings("ignore", message="torch.nn.utils.weight_norm` is deprecated")

# Local imports
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


# ---------------------------------------------------------------- #


print("Using MPS backend for Torch:", torch.backends.mps.is_available())
assert (
    torch.backends.mps.is_available()
), "Torch is not using MPS backend. Please ensure you have the correct setup for MPS."


# ---------------------------------------------------------------------- #

# SIMULATION_TEXT = """
# This man Ethan is so gay.
# I never knew he was this gay, until the day I met his mom.
# Here's a story about how I met his mom, and how I found out.

# It was a sunny day in the city, and I was walking down the street when I saw Ethan.
# He was wearing a bright pink shirt, tight jeans, and a pair of rainbow sneakers.
# He looked fabulous, as always.
# I waved at him, and he waved back with a big smile on his face.
# I walked over to him, and we started chatting.
# He told me about his latest fashion finds, his favorite makeup brands, and his plans for the weekend.
# He was so enthusiastic and passionate about everything he talked about.
# I couldn't help but admire his confidence and style.

# So I shot him.

# The end.
# """
SUBREDDIT_NAME = "AITAH"
SIMULATION_TEXT = f"{datetime.datetime.now().strftime('%H:%M')} - This is a test text for the BrainrotClipGenerator. I just have to say Ethan is kinda dumb. Andrew is amazing and hot and beautiful!! I love this man."
SIMULATION_VOICE = BrainrotClipGenerator.KOKORO_VOICES["british"][0]
SIMULATION_LANGUAGE = BrainrotClipGenerator.KOKORO_LANGUAGES["british"]


# ------------------------------------------------------------------------ #


if __name__ == "__main__":
    # exit()

    # ---------------------------------------------------------------- #
    # create reddit scraper instance
    reddit_scraper = RedditScraperBot(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_SECRET_KEY"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    # grab top 10 posts from the AITAH subreddit
    top_posts = reddit_scraper.get_top_subreddit_posts(SUBREDDIT_NAME, limit=10)
    print(f"Fetched {len(top_posts)} posts from {SUBREDDIT_NAME} subreddit.")
    the_chosen_one = top_posts[0]  # just take the first one for now
    print(f"Chosen post: {the_chosen_one.title}")

    # exxtract post information
    post_details = reddit_scraper.extract_post_details(the_chosen_one)
    print("Post details:", post_details)

    # check if it has an image
    post_media = reddit_scraper.extract_post_media(the_chosen_one)
    if post_media:
        print("Post has media:", post_media)
    else:
        print("Post has no media.")

    # extract post content
    post_content = the_chosen_one.selftext
    if not post_content:
        print("Post has no content. Exiting instead.")
        sys.exit(0)
    SIMULATION_TEXT = post_content

    # print out final results from this stage
    print("Final simulation text:\n", SIMULATION_TEXT)

    exit()

    # ---------------------------------------------------------------- #
    # if you want to manually select input text

    SIMULATION_TEXT = """
This is a test text for the BrainrotClipGenerator.
I just have to say Ethan is kinda dumb.
Andrew is amazing and hot and beautiful!!
I love this man.
    """

    # ---------------------------------------------------------------- #

    # create kokoro instance
    kokoro_pipeline = KPipeline(lang_code=SIMULATION_LANGUAGE, device="mps")

    # create an instance of the BrainrotClipGenerator
    video_generator = BrainrotClipGenerator(
        video_text=SIMULATION_TEXT,
        video_file=SOURCE_BACKGROUND_CLIP,
        kokoro_model=kokoro_pipeline,
        debug_output=True,
        framerate=TARGET_FRAMERATE,
        inter_segment_delay=0.1,
    )

    # split text into segments
    video_generator.split_text_into_segments(
        max_words=10,
        max_chars=1e9,
    )

    # generate audio segments
    def text_clip_modifier(text_settings: dict, text: str, segment_index: int) -> dict:
        # check length of words
        _word_count = len(text.split())
        if _word_count > 10:
            text_settings["font_size"] = 80 - 20 * min(1, _word_count / 20)

        # set width + height
        text_settings["width"] = TARGET_VIDEO_WIDTH * 0.8
        text_settings["height"] = TARGET_VIDEO_HEIGHT * 0.2
        return text_settings

    video_generator.generate_segments(
        TARGET_SEGMENTS_FOLDER,
        SIMULATION_VOICE,
    )

    # ---------------------------------------------------------------- #
    # modify the text clips to add a pop effect
    # Bouncy pop effect - more playful animation
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

    # apply the text effect to all segments
    video_generator.apply_text_effect(modifier_func)

    # ---------------------------------------------------------------- #

    # concatenate all the audio segment files into a single file
    video_generator.concat_audio_segment_files(
        TARGET_SEGMENTS_CONCAT_FILE,  # audio_segments=audio_segments
    )

    # ---------------------------------------------------------------------- #
    # extract only up until the audio length
    # and reduce framerate to 24fps
    moviepy.config.FFMPEG_BINARY = "ffmpeg"
    moviepy.config.IMAGEMAGICK_BINARY = "magick"

    # setup editor
    video_generator.setup()
    video_generator.composite_clips()

    # render the final video
    video_generator.render(TARGET_OUTPUT_FILE)
    video_generator.cleanup()
