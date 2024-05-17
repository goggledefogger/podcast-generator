# Podcast Generation Buddy

This project is an automated podcast generation buddy that streamlines the process of creating, editing, and publishing podcast episodes. It includes features for generating scripts, converting them to speech, and automating the audio editing process.

## Features

- Script generation based on topic, number of speakers, and duration
- Text-to-speech conversion using the `say` command on macOS
- Audio editing and stitching using SoX
- Simple content management system (CMS) for managing podcasts and episodes
- RESTful API for generating and regenerating podcast episodes
- Flask web server for serving static content and handling API requests

## Prerequisites

- macOS operating system
- Python 3.x
- OpenAI API key (for script generation)

## Installation

1. Clone the repository:
git clone https://github.com/goggledefogger/podcast-generator.git
Copy code
2. Navigate to the project directory:
cd podcast-generator
Copy code
3. Install the required Python dependencies:
pip install -r requirements.txt
Copy code
4. Install SoX for audio editing:
brew install sox
Copy code
5. Set up your OpenAI API key:
- Create a file named `.env` in the project root directory.
- Add the following line to the `.env` file:
  ```
  OPENAI_API_KEY=your_api_key_here
  ```
- Replace `your_api_key_here` with your actual OpenAI API key.

## Usage

1. Start the Flask web server:
python app.py
Copy code
2. Open a web browser and navigate to `http://localhost:5000`.

3. Use the provided interface to create and manage podcasts and episodes.

4. To create a new episode:
- Click on the "Create Episode" button or link.
- Fill in the episode details (topic, number of speakers, duration).
- Click the "Create Episode" button to generate the episode.

5. The generated episode will be saved in the `episodes.json` file, and the audio will be saved in the `audio_output` directory.

6. To regenerate an existing episode:
- Make a POST request to `/api/episodes/:episodeId/regenerate` with the appropriate episode ID.
- The episode will be regenerated with new script and audio.

## Project Structure

- `app.py`: Flask web server for serving static content and handling API requests.
- `script_generation.py`: Module for generating scripts using the OpenAI API.
- `audio_editing.py`: Module for converting scripts to speech and stitching audio files.
- `public/`: Directory for storing static content (HTML, CSS, JavaScript).
- `index.html`: Frontend HTML file for the CMS.
- `script.js`: Frontend JavaScript file for interacting with the backend API.
- `data/`: Directory for storing podcast and episode data.
- `podcasts.json`: JSON file for storing podcast data.
- `episodes.json`: JSON file for storing episode data.
- `audio_output/`: Directory for storing generated audio files.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please create an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
