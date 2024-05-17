import os
import subprocess

def convert_script_to_speech(script, output_dir):
    # Split the script into lines
    lines = script.split("\n")
    audio_files = []

    for i, line in enumerate(lines):
        output_file = f"{output_dir}/line_{i}.wav"
        cmd = f"say -o {output_file} --data-format=LEF32@32000 '{line}'"
        subprocess.call(cmd, shell=True)
        audio_files.append(output_file)

    return audio_files

def stitch_audio_files(audio_files, output_file):
    # Join the audio files with a space between them
    input_files = " ".join(audio_files)
    cmd = f"sox {input_files} {output_file}"
    subprocess.call(cmd, shell=True)
    return output_file
