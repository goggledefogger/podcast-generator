import os
import subprocess
import logging

def convert_script_to_speech(script, output_dir):
    lines = script.split("\n")
    audio_files = []

    for i, line in enumerate(lines):
        output_file = f"{output_dir}/line_{i}.wav"
        cmd = ["say", "-o", output_file, "--data-format=LEF32@32000", line]  # Command as a list

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error running 'say' command: {result.stderr}")
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")

        audio_files.append(output_file)

    return audio_files

def stitch_audio_files(audio_files, output_file):
    # Join the audio files with a space between them
    input_files = " ".join(audio_files)
    cmd = f"sox {input_files} {output_file}"
    subprocess.call(cmd, shell=True)
    return output_file
