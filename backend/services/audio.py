from kokoro import KPipeline

import json
from pathlib import Path
from typing import Dict, List, Tuple


import torch
import scipy.signal as signal
import soundfile as sf
import numpy as np

# -------------------------------------------------------------------- #

print("Using MPS backend for Torch:", torch.backends.mps.is_available())
assert (
    torch.backends.mps.is_available()
), "Torch is not using MPS backend. Please ensure you have the correct setup for MPS."

KOKORO_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


# -------------------------------------------------------------------- #
# constants

KOKORO_SAMPLING_RATE = 24000
KOKORO_LANGUAGES = {
    "american": "a",
    "british": "b",
    "french": "f",
    "japanese": "j",
}
KOKORO_LANGUAGE_INVERSE = {v: k for k, v in KOKORO_LANGUAGES.items()}
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

ASSETS_GENERATED_AUDIO = Path("assets/audio/generated")
TARGET_RATE = 44100  # Target sample rate for audio files


# -------------------------------------------------------------------- #
# utils

def create_kokoro_pipeline(language: str):
    """
    Create a Kokoro pipeline for generating transcripts from audio segments.

    :param voice: The voice model to use for transcription
    :return: KPipeline instance configured with the specified voice
    """
    try:
        pipeline = KPipeline(lang_code=language, device=KOKORO_DEVICE)
        return pipeline
    except Exception as e:
        raise RuntimeError(f"Failed to create Kokoro pipeline: {e}")

