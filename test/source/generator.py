from moviepy import TextClip
from kokoro import KPipeline


import re
import os
import numpy as np
import soundfile as sf
import scipy.signal as signal

import moviepy

from source.globals import (
    TARGET_VIDEO_WIDTH,
    TARGET_VIDEO_HEIGHT,
    SOURCE_FONT_FILE,
    DEFAULT_RENDER_OPTIONS,
)


# ---------------------------------------------------------------- #


class BrainrotClipGenerator:

    # ---------------------------------------------------- #
    # constants

    KOKORO_SAMPLE_RATE = 24000

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

    # ---------------------------------------------------- #
    # default settings for text clips

    def __init__(
        self,
        video_text: str,
        video_file: str,
        kokoro_model: KPipeline,
        debug_output=False,
        framerate=30,
        inter_segment_delay=0.1,
    ):
        """
        Initialize the BrainrotClipGenerator with a video file and debug output option.

        :param video_file: Path to the video file.
        :param debug_output: If True, will print debug information.

        """
        self._video_text = video_text
        self.video_file = video_file
        self.debug_output = debug_output
        self.kokoro_model = kokoro_model
        self.framerate = framerate

        self._inter_segment_delay = inter_segment_delay
        self._generated_text_segments = []
        self._video_clip = None
        self._video_dimensions = [0, 0]
        self._scale_factor = 1.0
        self._video_segments = {}

        self._concatenated_audio_duration = 0.0
        self._concatenated_audio_file = ""

        self._composite_clip = None

    # ---------------------------------------------------- #
    # main methods

    def setup(self):
        """
        Set up the generator with a new video file.

        :param video_file: Path to the new video file.
        """
        if not os.path.exists(self.video_file):
            raise FileNotFoundError(f"Video file not found: {self.video_file}")
        self._video_clip = moviepy.VideoFileClip(self.video_file)
        if self.debug_output:
            print(
                f"Video clip loaded: {self.video_file} ({self._video_clip.duration:.2f}s)"
            )

        # grab dimensions of video
        self._video_dimensions = list(self._video_clip.size)
        if self.debug_output:
            print(
                f"Video dimensions: {self._video_dimensions[0]}x{self._video_dimensions[1]}"
            )

        # calculate scale factor
        self._scale_factor = TARGET_VIDEO_HEIGHT / self._video_dimensions[1]
        __new_width = int(self._video_dimensions[0] * self._scale_factor)
        self._video_clip = self._video_clip.resized(height=TARGET_VIDEO_HEIGHT)
        if self.debug_output:
            print(
                f"Video clip resized to: {__new_width}x{TARGET_VIDEO_HEIGHT} "
                f"(scale factor: {self._scale_factor:.2f})"
            )

        # crop to target width
        if __new_width > TARGET_VIDEO_WIDTH:
            x_offset = (__new_width - TARGET_VIDEO_WIDTH) // 2
            self._video_clip = self._video_clip.cropped(
                x1=x_offset,
                y1=0,
                x2=x_offset + TARGET_VIDEO_WIDTH,
                y2=TARGET_VIDEO_HEIGHT,
            )
            if self.debug_output:
                print(
                    f"Video clip cropped to: {TARGET_VIDEO_WIDTH}x{TARGET_VIDEO_HEIGHT} "
                    f"(x_offset: {x_offset})"
                )
        else:
            if self.debug_output:
                print(
                    f"Video clip does not need cropping: {__new_width}x{TARGET_VIDEO_HEIGHT} "
                    f"(x_offset: 0)"
                )

        # get audio to be (audio length + 1)
        self._video_clip = self._video_clip.subclipped(
            0, self._concatenated_audio_duration + 1
        )

        # set target fps
        self._video_clip = self._video_clip.with_fps(self.framerate)

    def split_text_into_segments(self, max_words: int, max_chars: int) -> list:
        """
        Split the input text into manageable segments with constraints on:
        - Maximum number of words per segment
        - Maximum number of characters per segment

        When a segment exceeds max_length characters, the entire word that causes
        the overflow is removed and placed in the next segment.

        :param max_words: Maximum number of words per segment
        :param max_length: Maximum number of characters per segment
        :return: List of text segments
        """
        # First split by sentences (as in the original implementation)
        initial_splits = []
        for paragraph in self._video_text.splitlines():
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Split by sentence-ending punctuation, retain the symbols
            sentences = [
                s.strip() for s in re.findall(r"[^.?!]+[.?!]?", paragraph) if s.strip()
            ]
            initial_splits.extend(sentences)

        # Now apply word and character constraints to each sentence
        final_segments = []
        for sentence in initial_splits:
            words = sentence.split()

            if len(words) <= max_words and len(sentence) <= max_chars:
                # Sentence is already within limits, add it as-is
                final_segments.append(sentence)
                continue

            # Need to split this sentence further
            current_segment = []
            current_word_count = 0

            for word in words:
                # Check if adding this word would exceed limits
                if current_word_count + 1 > max_words:
                    # Word limit reached, finalize current segment
                    final_segments.append(" ".join(current_segment))
                    current_segment = [word]
                    current_word_count = 1
                else:
                    # Check character limit with the new word
                    potential_segment = (
                        " ".join(current_segment + [word]) if current_segment else word
                    )
                    if len(potential_segment) > max_chars:
                        # Character limit reached, finalize current segment
                        if current_segment:  # Only add if there's content
                            final_segments.append(" ".join(current_segment))
                        current_segment = [word]
                        current_word_count = 1
                    else:
                        # Word fits within limits, add it
                        current_segment.append(word)
                        current_word_count += 1

            # Add any remaining content in the last segment
            if current_segment:
                final_segments.append(" ".join(current_segment))

        # Store and return the result
        self._generated_text_segments = final_segments

        if self.debug_output:
            print(
                f"Split text into {len(self._generated_text_segments)} segments: "
                f"{self._generated_text_segments[:5]}..."  # Show first 5 segments
            )

        return self._generated_text_segments

    def generate_segments(
        self,
        folder_path: str,
        voice: str,
        text_clip_settings: dict = None,
    ) -> list:
        """
        Segment the input text into manageable chunks.
        This is a placeholder function; you can implement your own logic.
        """

        # Normalize clip settings
        if text_clip_settings is None:
            text_clip_settings = BrainrotClipGenerator.DEFAULT_TEXT_CLIP_SETTINGS.copy()
        elif not isinstance(text_clip_settings, dict):
            raise ValueError(
                "text_clip_settings must be a dictionary. "
                "Use BrainrotClipGenerator.DEFAULT_TEXT_CLIP_SETTINGS as a template."
            )

        # create the folder if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for key in BrainrotClipGenerator.DEFAULT_TEXT_CLIP_SETTINGS:
            if key not in text_clip_settings:
                text_clip_settings[key] = (
                    BrainrotClipGenerator.DEFAULT_TEXT_CLIP_SETTINGS[key]
                )

        # generate all the audio files
        segments = {}
        duration = 0.0
        for i, text in enumerate(self._generated_text_segments):

            # generate audio for the text segment
            audio_segment = self.kokoro_model(text, voice=voice)
            if not audio_segment:
                if self.debug_output:
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

            # Resample to 44100Hz
            target_rate = 44100
            new_length = int(
                len(raw_audio) * target_rate / BrainrotClipGenerator.KOKORO_SAMPLE_RATE
            )
            resampled_audio = signal.resample(raw_audio, new_length)

            # Normalize if needed
            max_amplitude = np.max(np.abs(resampled_audio))
            if max_amplitude > 0 and max_amplitude < 0.1:
                if self.debug_output:
                    print(
                        f"Segment {i} audio is quiet (max amplitude: {max_amplitude:.4f}), normalizing..."
                    )
                resampled_audio = resampled_audio / max_amplitude * 0.8

            # Save audio segment directly at 44100Hz
            segment_file = os.path.join(folder_path, f"segment_{i}.wav")
            sf.write(segment_file, resampled_audio, target_rate)
            resampled_duration = len(resampled_audio) / target_rate

            # Use resampled duration for timing
            segment_duration = resampled_duration
            duration += segment_duration

            # create a text clip
            text_clip = (
                TextClip(text=text, **text_clip_settings)
                .with_position(("center", "center"), relative=True)
                .with_start(duration - segment_duration)
                .with_duration(segment_duration)
            )

            # Append segment information
            segments[i] = {
                "index": i,
                "text": text,
                "file": str(segment_file),
                "duration": segment_duration,
                "start_time": duration - segment_duration,
                "end_time": duration,
                "kokoro_voice": voice,
                "kokoro_language": self.kokoro_model.lang_code,
                "text_clip": text_clip,
            }

            if self.debug_output:
                print(
                    f"Generated segment {i}: {text} ({segment_duration:.2f}s) "
                    f"saved to {segment_file}"
                )
        if self.debug_output:
            print(
                f"Generated {len(segments)} segments with total duration: {duration:.2f}s"
            )

        self._video_segments = segments
        return segments

    def concat_audio_segment_files(
        self, target_file: str, segments: list = None
    ) -> float:
        if segments is None:
            segments = self._video_segments

        if not segments:
            raise ValueError("No segments to concatenate.")

        raw_audio = []
        target_rate = 44100  # Use 44100Hz consistently

        # Create silence array for the delay (filled with zeros)
        silence_samples = int(
            self._inter_segment_delay * target_rate
        )  # Use target_rate
        silence = np.zeros((silence_samples,), dtype=np.float32)
        duration = 0.0

        for i, segment in segments.items():
            segment_file = segment["file"]
            if not os.path.exists(segment_file):
                if self.debug_output:
                    print(
                        f"Warning: Segment file {segment_file} does not exist. Skipping."
                    )
                continue

            # Load the audio file
            audio_data, sample_rate = sf.read(segment_file)
            if sample_rate != target_rate:
                if self.debug_output:
                    print(
                        f"Warning: Sample rate mismatch in segment {i} ({sample_rate}Hz vs {target_rate}Hz)"
                    )

            raw_audio.append(audio_data)

            # Add silence after each segment (except the last one)
            if i < len(segments) - 1:
                raw_audio.append(silence)

        # Save the concatenated audio with target_rate
        sf.write(target_file, np.concatenate(raw_audio, axis=0), target_rate)
        if self.debug_output:
            print(f"Saved concatenated audio at {target_rate}Hz")

        # Calculate the total duration
        duration = (
            sum(segment["duration"] for segment in segments.values())
            + (len(segments) - 1) * self._inter_segment_delay
        )

        self._concatenated_audio_file = target_file
        self._concatenated_audio_duration = duration
        if self.debug_output:
            print(
                f"Concatenated audio saved to {target_file} with duration {duration:.2f}s"
            )
        return duration

    # ---------------------------------------------------- #
    # rendering functions

    def composite_clips(self):
        """
        Render the video with the generated segments.
        This is a placeholder function; you can implement your own logic.
        """
        if self._video_clip is None:
            raise ValueError("Video clip not set up. Call setup() first.")

        if not self._video_segments:
            raise ValueError("No segments generated. Call generate_segments() first.")

        if self.debug_output:
            print("Rendering video with segments...")

        text_clips = [
            segment["text_clip"] for key, segment in self._video_segments.items()
        ]
        composite_clip = moviepy.CompositeVideoClip([self._video_clip] + text_clips)

        # add audio to video
        if self._concatenated_audio_file:
            audio_clip = moviepy.AudioFileClip(self._concatenated_audio_file)
            composite_clip = composite_clip.with_audio(audio_clip)
            if self.debug_output:
                print("Added audio to video clip.")
        else:
            if self.debug_output:
                print("No audio file found. Video will be silent.")

        # return the composite clip
        self._composite_clip = composite_clip
        if self.debug_output:
            print(
                f"Composite video clip created with {len(text_clips)} text clips "
                f"and duration {composite_clip.duration:.2f}s"
            )
        return composite_clip

    def render(self, output_file: str, **options: dict):
        """
        Render the composite video clip to a file.

        :param output_file: Path to the output video file.
        """
        if self._composite_clip is None:
            raise ValueError(
                "Composite clip not created. Call composite_clips() first."
            )
        # Ensure all options are set
        for key in DEFAULT_RENDER_OPTIONS:
            if key not in options:
                options[key] = DEFAULT_RENDER_OPTIONS[key]
        if self.debug_output:
            print(f"Rendering composite clip to {output_file}...")

        # Write the video file
        self._composite_clip.write_videofile(output_file, **options)
        if self.debug_output:
            print(f"Video rendered successfully to {output_file}.")

    def cleanup(self):
        """
        Clean up resources used by the generator.
        """
        if self._video_clip:
            self._video_clip.close()
            self._video_clip = None
            if self.debug_output:
                print("Video clip resources cleaned up.")

        if self._composite_clip:
            self._composite_clip.close()
            self._composite_clip = None
            if self.debug_output:
                print("Composite clip resources cleaned up.")

        # delete generated audio files
        if self._concatenated_audio_file and os.path.exists(
            self._concatenated_audio_file
        ):
            os.remove(self._concatenated_audio_file)
            if self.debug_output:
                print(
                    f"Removed concatenated audio file: {self._concatenated_audio_file}"
                )
        else:
            if self.debug_output:
                print("No concatenated audio file to remove.")
        # delete all segment files
        for segment in self._video_segments.values():
            segment_file = segment["file"]
            if os.path.exists(segment_file):
                os.remove(segment_file)
                if self.debug_output:
                    print(f"Removed segment file: {segment_file}")
            else:
                if self.debug_output:
                    print(f"Segment file does not exist: {segment_file}")

        # Clear segments
        self._video_segments = {}
        if self.debug_output:
            print("Video segments cleared.")

        print("Cleanup complete. All temporary files removed.")

    # ---------------------------------------------------- #
    # misc tools

    def apply_text_effect(self, apply_func: callable, **kwargs) -> None:
        """
        Apply a text effect to the video clip.

        :param apply_func: Function to apply the effect.
        :param kwargs: Additional arguments for the effect function.
        """

        # output a warning if no segments exist
        if not self._video_segments:
            print("Warning: No video segments available. Cannot apply text effect.")
        if self.debug_output:
            print(f"Applying text effect with {apply_func.__name__}...")

        # for all segments generated, apply the text effect
        for key, val in self._video_segments.items():
            self._video_segments[key] = apply_func(val, **kwargs)
