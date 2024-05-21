import os
import subprocess
import re
import logging
from typing import List

# Define a list of available voices on macOS
AVAILABLE_VOICES = ["Alex", "Ava", "Samantha"]

# Updated pattern to capture more accurately
pattern = re.compile(r"^([\w\s]+):(.*)")

def convert_script_to_speech(script: str, output_dir: str) -> List[str]:
    lines = script.split("\n")
    audio_files = []
    aiff_files = []
    speaker_voice_map = {}

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        logging.info(f"Processing line {i}: {line}")
        pattern_match = pattern.match(line)
        if pattern_match:
            speaker, text = pattern_match.groups()
            speaker = speaker.strip()
            text = text.strip()
            logging.info(f"Matched speaker: '{speaker}', text: '{text}'")

            # Assign a voice to the speaker if not already assigned
            if speaker not in speaker_voice_map:
                assigned_voice = AVAILABLE_VOICES[len(speaker_voice_map) % len(AVAILABLE_VOICES)]
                speaker_voice_map[speaker] = assigned_voice
                logging.info(f"Assigned voice '{assigned_voice}' to speaker '{speaker}'")

            # Get the assigned voice for the speaker
            voice = speaker_voice_map[speaker]
        else:
            # If the line doesn't match the pattern, skip it (no voice assignment)
            logging.info(f"Line didn't match pattern, skipping: '{line}'")
            continue

        # Generate the audio file using the `say` command without the speaker name
        aiff_file_path = os.path.join(output_dir, f"line_{i}.aiff")
        wav_file_path = os.path.join(output_dir, f"line_{i}.wav")
        command = f'say -v {voice} "{text}" -o {aiff_file_path}'
        logging.info(f"Running command: {command}")

        try:
            subprocess.run(command, shell=True, check=True)

            # Convert AIFF to WAV
            convert_command = f'sox {aiff_file_path} {wav_file_path}'
            logging.info(f"Running convert command: {convert_command}")
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

    if not audio_files:
        logging.error("No audio files were generated.")
        return []

    return audio_files

def stitch_audio_files(audio_files: List[str], output_file_path: str) -> str:
    if not audio_files:
        logging.error("No audio files to stitch.")
        raise ValueError("No audio files to stitch.")

    try:
        # Use `sox` to stitch audio files together
        command = f'sox {" ".join(audio_files)} {output_file_path}'
        logging.info(f"Running stitch command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error stitching audio files: {e}")
        raise

    return output_file_path
