import json
import os
import logging
import uuid
from flask import Flask, request, jsonify, send_from_directory, Response
from script_generation import generate_script
from audio_editing import convert_script_to_speech, stitch_audio_files
from llm_utils import call_llm, get_prompt, SYSTEM_PROMPT
from feedgen.feed import FeedGenerator

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

    # Convert podcast_id to a string for consistency in comparison
    podcast_episodes = [episode for episode in episodes if episode["podcast_id"] == str(podcast_id)]
    for episode in podcast_episodes:
        # Ensure each episode has a title field
        episode["title"] = episode.get("topic", "No title available")
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

@app.route("/api/episodes/<episode_id>", methods=["GET"])
def get_episode(episode_id):
    episodes = load_data(EPISODES_FILE)
    episode = next((ep for ep in episodes if ep["id"] == episode_id), None)
    if episode:
        logger.info(f"Retrieved episode with topic: {episode['topic']}")
        return jsonify(episode), 200
    return jsonify({"error": "Episode not found"}), 404

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

    # Ensure the episode has a podcast_id attribute
    if 'podcast_id' not in episode_data:
        return jsonify({"error": "podcast_id is required"}), 400

    episodes = load_data(EPISODES_FILE)
    episodes.append(episode_data)
    save_data(EPISODES_FILE, episodes)

    logger.info(f"Episode created with audio file: {episode_audio_path}")
    return jsonify(episode_data), 201

@app.route("/api/episodes/<episode_id>", methods=["PUT"])
def update_episode(episode_id):
    episode_data = request.get_json()
    episodes = load_data(EPISODES_FILE)

    for episode in episodes:
        if episode['id'] == episode_id:
            episode.update(episode_data)
            save_data(EPISODES_FILE, episodes)
            return jsonify({"message": "Episode updated"}), 200

    return jsonify({"error": "Episode not found"}), 404

@app.route("/api/generate/<field>", methods=["POST"])
def generate_field(field):
    generated_content = generate_field_content(field)
    return jsonify({"content": generated_content})

def generate_field_content(field_name):
    # Define context based on field name
    context = {}
    if 'episode' in field_name:
        context = {
            "topic": "example topic",
            "duration": 10,
            "num_speakers": 2,
            "plural": "s",
            "speakers": "Speaker 1 and Speaker 2",
            "guest_name": "Guest"
        }
    elif 'podcast' in field_name:
        context = {
            "topic": "example topic",
            "author_name": "Author"
        }

    prompt = get_prompt(field_name, context)
    if prompt is None:
        return "Prompt not found for the specified field."
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    return call_llm(messages)


def generate_rss_feed(podcast_id):
    episodes = load_data(EPISODES_FILE)
    podcast_episodes = [ep for ep in episodes if ep['podcast_id'] == podcast_id]

    fg = FeedGenerator()
    podcasts = load_data(PODCASTS_FILE)
    podcast = next((p for p in podcasts if p['id'] == podcast_id), None)

    if not podcast:
        return "Podcast not found", 404

    fg.id(f'http://example.com/podcast/{podcast_id}')
    fg.title(podcast['title'])
    fg.author({'name': podcast.get('author', 'Unknown'), 'email': podcast.get('email', 'author@example.com')})
    fg.link(href='http://example.com', rel='alternate')
    fg.logo('http://example.com/logo.jpg')
    fg.subtitle(podcast.get('subtitle', ''))
    fg.link(href=f'http://example.com/podcast/{podcast_id}/rss', rel='self')
    fg.language('en')

    for ep in podcast_episodes:
        fe = fg.add_entry()
        fe.id(ep['id'])
        fe.title(ep['title'])
        fe.description(ep['description'])
        fe.enclosure(ep['audio_file'], 0, 'audio/mpeg')

    return fg.rss_str(pretty=True)

@app.route("/api/podcast/<podcast_id>/rss", methods=["GET"])
def get_podcast_rss(podcast_id):
    rss_feed = generate_rss_feed(podcast_id)
    if isinstance(rss_feed, tuple):
        return jsonify({"error": rss_feed[0]}), rss_feed[1]
    return Response(rss_feed, mimetype='application/rss+xml')

if __name__ == "__main__":
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    app.run(debug=True)
