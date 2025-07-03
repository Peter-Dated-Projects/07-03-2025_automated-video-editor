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
import cv2
import moviepy
from moviepy import (
    VideoFileClip,
    TextClip,
    ImageSequenceClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
)


# for text to speech
from kokoro import KPipeline
import soundfile as sf

import torch
import numpy as np

import re
import scipy.signal as signal
import warnings

# Filter out specific PyTorch warnings
warnings.filterwarnings(
    "ignore", message="dropout option adds dropout after all but last recurrent layer"
)
warnings.filterwarnings("ignore", message="torch.nn.utils.weight_norm` is deprecated")

# Alternatively, to suppress all warnings (not recommended for development)
# warnings.filterwarnings("ignore")

# ---------------------------------------------------------------- #
KOKORO_SAMPLE_RATE = 24000

SOURCE_BACKGROUND_CLIP = "assets/bgclip1.mp4"
SOURCE_FONT_FILE = "assets/Roboto-Bold.ttf"

TARGET_OUTPUT_FILE = "assets/target_output.mp4"
TARGET_SEGMENTS_FOLDER = "assets/segments"
TARGET_SEGMENTS_CONCAT_FILE = "assets/concatenated_audio.wav"

# instagram video dimensions
TARGET_VIDEO_WIDTH = 1080
TARGET_VIDEO_HEIGHT = 1920
TARGET_FRAMERATE = 30

KOKORO_LANGUAGES = {
    "american": "a",
    "british": "b",
    "french": "f",
    "japanese": "j",
}
KOKORO_VOICES = {
    "american": [
        "af_sarah",
        "af_olivia",
        "af_mia",
        "af_james",
        "am_adam",
        "am_michael",
    ],
    "british": [
        "bm_george",
        "bm_lewis",
        "bf_emma",
        "bf_isabella",
    ],
}
DEFAULT_TEXT_CLIP_SETTINGS = {
    "font": SOURCE_FONT_FILE,
    "font_size": 80,
    "size": (TARGET_VIDEO_WIDTH, TARGET_VIDEO_HEIGHT),
    "color": "white",
    "bg_color": "#00000000",  # Fully transparent (the last 00 is alpha=0)
    "method": "caption",  # or "label"
    # for text border
    "stroke_width": 3,
    "stroke_color": "black",
    # align
    "text_align": "center",
    "horizontal_align": "center",
    "vertical_align": "center",
    # spacing
    "interline": 5,
    "transparent": True,
    "duration": None,
}

print("Using MPS backend for Torch:", torch.backends.mps.is_available())
assert (
    torch.backends.mps.is_available()
), "Torch is not using MPS backend. Please ensure you have the correct setup for MPS."


# ---------------------------------------------------------------------- #


def generate_segments(
    text: str,
    folder_path: str,
    kokoro_model: KPipeline,
    voice: str,
    text_clip_settings: dict,
) -> list:
    """
    Segment the input text into manageable chunks.
    This is a placeholder function; you can implement your own logic.
    """
    # Split by sentence-ending punctuation, but retain the symbols.
    _splits = [s.strip() for s in re.findall(r"[^.?!]+[.?!]?", text) if s.strip()]

    # create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for key in DEFAULT_TEXT_CLIP_SETTINGS:
        if key not in text_clip_settings:
            text_clip_settings[key] = DEFAULT_TEXT_CLIP_SETTINGS[key]

    # generate all the audio files
    segments = []
    duration = 0.0
    for i, text in enumerate(_splits):

        # generate audio for the text segment
        audio_segment = kokoro_model(text, voice=voice)
        if not audio_segment:
            print(f"Warning: No audio generated for segment {i}. Skipping.")
            continue

        concat = []
        for _, _, aseg in audio_segment:
            # Ensure aseg is a tensor or numpy array
            if hasattr(aseg, "numpy"):
                audio_segment = aseg.numpy()
            else:
                audio_segment = aseg
            concat.append(audio_segment)

        # Concatenate the segments
        raw_audio = np.concatenate(concat, axis=0)

        # Calculate original duration (needed for timing)
        original_duration = len(raw_audio) / KOKORO_SAMPLE_RATE

        # Resample to 44100Hz
        target_rate = 44100
        new_length = int(len(raw_audio) * target_rate / KOKORO_SAMPLE_RATE)
        resampled_audio = signal.resample(raw_audio, new_length)

        # Normalize if needed
        max_amplitude = np.max(np.abs(resampled_audio))
        if max_amplitude > 0 and max_amplitude < 0.1:
            print(
                f"Segment {i} audio is quiet (max amplitude: {max_amplitude:.4f}), normalizing..."
            )
            resampled_audio = resampled_audio / max_amplitude * 0.8

        # Save audio segment directly at 44100Hz
        segment_file = os.path.join(folder_path, f"segment_{i}.wav")
        sf.write(segment_file, resampled_audio, target_rate)

        # Use original duration for timing calculations
        segment_duration = original_duration
        duration += segment_duration

        # create a text clip
        text_clip = (
            TextClip(text=text, **text_clip_settings)
            .with_position(("center", "center"), relative=True)
            .with_start(duration - segment_duration)
            .with_duration(segment_duration)
        )

        segments.append(
            {
                "index": i,
                "text": text,
                "file": str(segment_file),
                "duration": segment_duration,
                "start_time": duration - segment_duration,
                "end_time": duration,
                "kokoro_voice": voice,
                "kokoro_language": kokoro_model.lang_code,
                "text_clip": text_clip,
            }
        )

    return segments


def concat_audio_segment_files(
    segments: list, target_file: str, delay: float = 0.1
) -> float:
    if not segments:
        raise ValueError("No segments to concatenate.")

    raw_audio = []
    target_rate = 44100  # Use 44100Hz consistently

    # Create silence array for the delay (filled with zeros)
    silence_samples = int(delay * target_rate)  # Use target_rate
    silence = np.zeros((silence_samples,), dtype=np.float32)
    duration = 0.0

    for i, segment in enumerate(segments):
        segment_file = segment["file"]
        if not os.path.exists(segment_file):
            print(f"Warning: Segment file {segment_file} does not exist. Skipping.")
            continue

        # Load the audio file
        audio_data, sample_rate = sf.read(segment_file)
        if sample_rate != target_rate:
            print(
                f"Warning: Sample rate mismatch in segment {i} ({sample_rate}Hz vs {target_rate}Hz)"
            )

        raw_audio.append(audio_data)

        # Add silence after each segment (except the last one)
        if i < len(segments) - 1:
            raw_audio.append(silence)

    # Save the concatenated audio with target_rate
    sf.write(target_file, np.concatenate(raw_audio, axis=0), target_rate)
    print(f"Saved concatenated audio at {target_rate}Hz")

    # Calculate the total duration
    duration = (
        sum(segment["duration"] for segment in segments) + (len(segments) - 1) * delay
    )
    return duration


# ---------------------------------------------------------------------- #

SIMULATION_TEXT = "This man Ethan is so gay."
# SIMULATION_TEXT = "こんにちは、世界！"

SIMULATION_VOICE = KOKORO_VOICES["british"][0]
# SIMULATION_VOICE = "jf_nanami"

SIMULATION_LANGUAGE = KOKORO_LANGUAGES["british"]
# SIMULATION_LANGUAGE = KOKORO_LANGUAGES["japanese"]


# ------------------------------------------------------------------------ #

# create a japanese kokoro pipeline
kokoro_pipeline = KPipeline(lang_code=SIMULATION_LANGUAGE, device="mps")
# generate audio for the text
audio_segments = generate_segments(
    SIMULATION_TEXT,
    TARGET_SEGMENTS_FOLDER,
    kokoro_pipeline,
    SIMULATION_VOICE,
    DEFAULT_TEXT_CLIP_SETTINGS,
)

# concatenate all the audio segment files into a single file
audio_duration = concat_audio_segment_files(
    audio_segments,
    TARGET_SEGMENTS_CONCAT_FILE,
)

# ---------------------------------------------------------------------- #
# extract only up until the audio length
# and reduce framerate to 24fps
moviepy.config.FFMPEG_BINARY = "ffmpeg"
moviepy.config.IMAGEMAGICK_BINARY = "magick"

print("Loading video clip:", SOURCE_BACKGROUND_CLIP)
clip = VideoFileClip(SOURCE_BACKGROUND_CLIP)

# Get original dimensions
original_width, original_height = clip.size
print(f"Original video dimensions: {original_width}x{original_height}")

# Scale to target height while maintaining aspect ratio
scale_factor = TARGET_VIDEO_HEIGHT / original_height
new_width = int(original_width * scale_factor)
clip = clip.resized(height=TARGET_VIDEO_HEIGHT)
print(f"Scaled video dimensions: {new_width}x{TARGET_VIDEO_HEIGHT}")

# Crop to target width (centered)
if new_width > TARGET_VIDEO_WIDTH:
    # Calculate x-offset for center crop
    x_offset = (new_width - TARGET_VIDEO_WIDTH) // 2
    clip = clip.cropped(
        x1=x_offset, y1=0, x2=x_offset + TARGET_VIDEO_WIDTH, y2=TARGET_VIDEO_HEIGHT
    )
    print(f"Cropped video dimensions: {TARGET_VIDEO_WIDTH}x{TARGET_VIDEO_HEIGHT}")
else:
    print("Warning: Scaled width is smaller than target width. No cropping performed.")

clip = clip.subclipped(0, audio_duration + 1.0)  # Trim to match audio
clip = clip.with_fps(TARGET_FRAMERATE)  # Set desired framerate

# add rendered text clips to the video
text_clips = [segment["text_clip"] for segment in audio_segments]
composite_clip = CompositeVideoClip([clip] + text_clips)

# add audio to video
audio_clip = AudioFileClip(TARGET_SEGMENTS_CONCAT_FILE)
composite_clip = composite_clip.with_audio(audio_clip)
print("Added audio to video clip.")

# write final video to file
composite_clip.write_videofile(
    TARGET_OUTPUT_FILE,
    codec="libx264",
    audio_codec="aac",
    audio_bitrate="192k",
    fps=TARGET_FRAMERATE,
    preset="medium",
    audio_fps=44100,
    ffmpeg_params=["-strict", "-2", "-ar", "44100", "-ac", "2"],  # Force audio params
)

print(f"Final video saved to {TARGET_OUTPUT_FILE}")

# cleanup files
if os.path.exists(TARGET_SEGMENTS_CONCAT_FILE):
    os.remove(TARGET_SEGMENTS_CONCAT_FILE)
    print(f"Removed temporary audio file: {TARGET_SEGMENTS_CONCAT_FILE}")
for segment in audio_segments:
    segment_file = segment["file"]
    if os.path.exists(segment_file):
        os.remove(segment_file)
        print(f"Removed temporary audio segment file: {segment_file}")
print("Cleanup complete. All temporary files removed.")
