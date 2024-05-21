import json
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from script_generation import generate_script
from audio_editing import convert_script_to_speech, stitch_audio_files
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='public', static_url_path='')
PODCASTS_FILE = "db/podcasts.json"
EPISODES_FILE = "db/episodes.json"
AUDIO_OUTPUT_DIR = "audio_output"

def load_data(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump([], file)  # Create an empty JSON array
    with open(file_path, 'r') as file:
        return json.load(file)

def save_data(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        logging.info(f"Data saved to {file_path} successfully.")
    except Exception as e:
        logging.error(f"Failed to save data to {file_path}: {e}")

@app.route("/api/episodes", methods=["POST"])
def create_episode():
    episode_data = request.get_json()
    logger.info(f"Received episode data: {episode_data}")

    # Assign a unique ID to the episode
    episode_data["id"] = str(uuid.uuid4())

    script = generate_script(episode_data["topic"], episode_data["num_speakers"], episode_data["duration"])
    episode_data["script"] = script

    logger.info("Converting script to speech...")
    audio_files = convert_script_to_speech(script, AUDIO_OUTPUT_DIR)
    episode_audio_path = f"{AUDIO_OUTPUT_DIR}/episode_{episode_data['id']}.mp3"
    episode_audio = stitch_audio_files(audio_files, episode_audio_path)
    episode_data["audio_file"] = episode_audio_path

    episodes = load_data(EPISODES_FILE)
    episodes.append(episode_data)
    save_data(EPISODES_FILE, episodes)

    logger.info(f"Episode created with audio file: {episode_audio_path}")
    return jsonify(episode_data), 201

@app.route("/api/podcasts", methods=["GET"])
def get_podcasts():
    podcasts = load_data(PODCASTS_FILE)
    return jsonify(podcasts)

@app.route("/api/podcasts", methods=["POST"])
def create_podcast():
    podcast_data = request.get_json()
    logger.info(f"Received podcast data: {podcast_data}")

    # Assign a unique ID to the podcast
    podcast_data["id"] = str(uuid.uuid4())

    podcasts = load_data(PODCASTS_FILE)
    podcasts.append(podcast_data)
    save_data(PODCASTS_FILE, podcasts)

    logger.info(f"Podcast created with ID: {podcast_data['id']}")
    return jsonify(podcast_data), 201

@app.route("/api/podcasts/<string:podcast_id>/episodes", methods=["GET"])
def get_podcast_episodes(podcast_id):
    episodes = load_data(EPISODES_FILE)
    logging.info(f"Retrieving episodes for podcast with ID: {podcast_id}")
    logging.info(f"is the podcast ID a string or number: {type(podcast_id)}")
    podcast_episodes = [episode for episode in episodes if episode["podcast_id"] == podcast_id]
    logging.info(f"Found {len(podcast_episodes)} episodes for podcast with ID: {podcast_id}")
    return jsonify(podcast_episodes)

@app.route("/api/episodes/<string:episode_id>", methods=["DELETE"])
def delete_episode(episode_id):
    episodes = load_data(EPISODES_FILE)
    episodes = [episode for episode in episodes if episode["id"] != episode_id]

    save_data(EPISODES_FILE, episodes)
    logger.info(f"Episode with ID {episode_id} deleted.")
    return jsonify({"message": "Episode deleted"}), 200

@app.route('/audio_output/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_OUTPUT_DIR, filename)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    app.run(debug=True)
