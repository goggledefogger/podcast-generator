import json
import os
from flask import Flask, request, jsonify, send_from_directory
from script_generation import generate_script
from audio_editing import convert_script_to_speech, stitch_audio_files

app = Flask(__name__)
PODCASTS_FILE = "podcasts.json"
EPISODES_FILE = "episodes.json"
AUDIO_OUTPUT_DIR = "audio_output"

def load_data(file_name):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/podcasts", methods=["GET"])
def get_podcasts():
    podcasts = load_data(PODCASTS_FILE)
    return jsonify(podcasts)

@app.route("/api/podcasts", methods=["POST"])
def create_podcast():
    podcast = request.get_json()
    podcasts = load_data(PODCASTS_FILE)
    podcast["id"] = len(podcasts) + 1
    podcasts.append(podcast)
    save_data(PODCASTS_FILE, podcasts)
    return jsonify(podcast), 201

@app.route("/api/podcasts/<int:podcast_id>", methods=["PUT"])
def update_podcast(podcast_id):
    updated_podcast = request.get_json()
    podcasts = load_data(PODCASTS_FILE)
    for podcast in podcasts:
        if podcast["id"] == podcast_id:
            podcast.update(updated_podcast)
            break
    save_data(PODCASTS_FILE, podcasts)
    return jsonify(updated_podcast)

@app.route("/api/podcasts/<int:podcast_id>", methods=["DELETE"])
def delete_podcast(podcast_id):
    podcasts = load_data(PODCASTS_FILE)
    podcasts = [podcast for podcast in podcasts if podcast["id"] != podcast_id]
    save_data(PODCASTS_FILE, podcasts)
    return "", 204

@app.route("/api/podcasts/<int:podcast_id>/episodes", methods=["GET"])
def get_podcast_episodes(podcast_id):
    episodes = load_data(EPISODES_FILE)
    podcast_episodes = [episode for episode in episodes if episode["podcast_id"] == podcast_id]
    return jsonify(podcast_episodes)

@app.route("/api/episodes", methods=["POST"])
def create_episode():
    episode_data = request.get_json()
    episode = generate_episode(episode_data)
    episodes = load_data(EPISODES_FILE)
    episode["id"] = len(episodes) + 1
    episodes.append(episode)
    save_data(EPISODES_FILE, episodes)
    return jsonify(episode), 201

def generate_episode(episode_data):
    script = generate_script(episode_data["topic"], episode_data["num_speakers"], episode_data["duration"])
    episode_data["script"] = script

    audio_files = convert_script_to_speech(script, AUDIO_OUTPUT_DIR)
    episode_audio = stitch_audio_files(audio_files, f"{AUDIO_OUTPUT_DIR}/episode_{episode_data['id']}.mp3")
    episode_data["audio_file"] = episode_audio

    return episode_data

@app.route("/api/episodes/<int:episode_id>/regenerate", methods=["POST"])
def regenerate_episode(episode_id):
    episodes = load_data(EPISODES_FILE)
    episode = next((episode for episode in episodes if episode["id"] == episode_id), None)
    if episode:
        regenerated_episode = generate_episode(episode)
        episode.update(regenerated_episode)
        save_data(EPISODES_FILE, episodes)
        return jsonify({"message": "Episode regenerated successfully"})
    return jsonify({"message": "Episode not found"}), 404

# Update the route for serving static files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    return send_from_directory('public', path) # Serve from 'public'

if __name__ == "__main__":
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    app.run(debug=True)
