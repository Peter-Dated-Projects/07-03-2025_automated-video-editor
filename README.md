# Automated Video Editor

An automated video editing pipeline that converts input text into a narrated, captioned video. This project combines:

- **Kokoro TTS** for high-quality text-to-speech synthesis
- **MoviePy** (and OpenCV) for video processing and dynamic text overlays
- **.env configuration** for managing secrets and device settings

Ideal for creating short, social-media-ready videos (e.g., Instagram Reels) with synchronized audio and text captions.

---

## Features

- **Text Segmentation**: Splits input text into sentences or custom segments
- **TTS Audio Generation**: Uses Kokoro to synthesize speech in multiple languages and voices
- **Audio Concatenation**: Joins audio segments with configurable delays
- **Background Video Processing**:
  - Resizes and crops source video to target dimensions (e.g., 1080×1920 for vertical formats)
  - Extracts frames and re-encodes at specified frame rate
- **Dynamic Text Overlays**:
  - Renders caption clips aligned with audio timings
  - Customizable font, size, color, stroke, alignment, and inter-line spacing
- **Final Composition**: Merges video frames, text clips, and audio into a single output video

---

## Prerequisites

- **Python 3.7+**
- **FFmpeg** on your PATH
- **ImageMagick** (for TextClip) on your PATH or set `moviepy.config.IMAGEMAGICK_BINARY`
- **espeak-ng** (optional, for Kokoro G2P fallbacks)
- **Torch** with MPS or CUDA support (optional GPU acceleration)

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Peter-Dated-Projects/07-03-2025_automated-video-editor.git
   cd 07-03-2025_automated-video-editor
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .\.venv\\Scripts\\activate  # Windows
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**
   - macOS: `brew install ffmpeg imagemagick espeak-ng`
   - Ubuntu/Debian: `sudo apt install ffmpeg imagemagick espeak-ng`
   - Windows: Install FFmpeg and ImageMagick, add to PATH

5. **Configure environment variables**
   - Copy `.env.example` to `.env` and set any necessary keys (e.g., device overrides)

---

## Configuration

- **`TARGET_VIDEO_WIDTH`** and **`TARGET_VIDEO_HEIGHT`**: Output dimensions (pixels)
- **`TARGET_FRAMERATE`**: Output frame rate (fps)
- **`DEFAULT_TEXT_CLIP_SETTINGS`**: Customize font, size, color, background, stroke, alignment, and inter-line spacing
- **`KOKORO_LANGUAGES`** and **`KOKORO_VOICES`**: Map human-readable names to language codes and voice models

All settings are defined in `main.py` at the top of the file.

---

## Usage

1. **Place your assets**
   - Background video: `assets/bgclip1.mp4`
   - Font file: `assets/Roboto-Bold.ttf`

2. **Edit `SIMULATION_TEXT`**, `SIMULATION_VOICE`, and `SIMULATION_LANGUAGE` in `main.py` to your desired input.

3. **Run the script**
   ```bash
   python test/main.py
   ```

4. **Output**
   - Final video: `assets/target_output.mp4`
   - Intermediate audio segments: `assets/segments/segment_*.wav`
   - Concatenated audio: `assets/concatenated_audio.wav`

---

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

