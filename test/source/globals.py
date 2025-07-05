SOURCE_BACKGROUND_CLIP = "assets/bgclip1.mp4"
SOURCE_FONT_FILE = "assets/Roboto-Bold.ttf"

TARGET_OUTPUT_FILE = "assets/target_output.mp4"
TARGET_SEGMENTS_FOLDER = "assets/segments"
TARGET_SEGMENTS_CONCAT_FILE = "assets/concatenated_audio.wav"

# instagram video dimensions
TARGET_VIDEO_WIDTH = 1080
TARGET_VIDEO_HEIGHT = 1920
TARGET_FRAMERATE = 30

DEFAULT_RENDER_OPTIONS = {
    "codec": "libx264",
    "audio_codec": "aac",
    "audio_bitrate": "192k",
    "fps": TARGET_FRAMERATE,
    "preset": "medium",
    "audio_fps": 44100,
    "ffmpeg_params": [
        "-pix_fmt",
        "yuv420p",  # Ensure compatibility with most players
        "-movflags",
        "+faststart",  # Optimize for web streaming
    ],  # Force audio params
}
