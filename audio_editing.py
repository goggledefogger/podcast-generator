import os
import subprocess
import re
import logging
from typing import List

# Define a list of available voices on macOS
AVAILABLE_VOICES = ["Fred", "Samantha"]

pattern = re.compile(r"^\s*(\w+):(.*)")

def convert_script_to_speech(script: str, output_dir: str) -> List[str]:
    lines = script.split("\n")
    audio_files = []
    aiff_files = []
    speaker_voice_map = {}
    voice = AVAILABLE_VOICES[0]

    for i, line in enumerate(lines):
        pattern_match = pattern.match(line)
        if pattern_match:
            speaker, text = pattern_match.groups()
            speaker = speaker.strip()
            text = text.strip()

            # Assign a voice to the speaker if not already assigned
            if speaker not in speaker_voice_map:
                assigned_voice = AVAILABLE_VOICES[len(speaker_voice_map) % len(AVAILABLE_VOICES)]
                speaker_voice_map[speaker] = assigned_voice

            # Get the assigned voice for the speaker
            voice = speaker_voice_map[speaker]
        else:
            # If the line doesn't match the pattern, use the default voice and the entire line as text
            text = line.strip()

        # Generate the audio file using the `say` command
        aiff_file_path = os.path.join(output_dir, f"line_{i}.aiff")
        wav_file_path = os.path.join(output_dir, f"line_{i}.wav")
        command = f'say -v {voice} "{text}" -o {aiff_file_path}'

        try:
            subprocess.run(command, shell=True, check=True)

            # Convert AIFF to WAV
            convert_command = f'sox {aiff_file_path} {wav_file_path}'
            subprocess.run(convert_command, shell=True, check=True)

            audio_files.append(wav_file_path)
            aiff_files.append(aiff_file_path)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error generating or converting audio for line {i}: {e}")
            # If there's an error, clean up any created files
            if os.path.exists(aiff_file_path):
                os.remove(aiff_file_path)
            if os.path.exists(wav_file_path):
                os.remove(wav_file_path)

    # Clean up AIFF files after conversion
    for aiff_file in aiff_files:
        if os.path.exists(aiff_file):
            os.remove(aiff_file)

    return audio_files

def stitch_audio_files(audio_files: List[str], output_file_path: str) -> str:
    try:
        # Use `sox` to stitch audio files together
        command = f'sox {" ".join(audio_files)} {output_file_path}'
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error stitching audio files: {e}")
        raise

    return output_file_path
