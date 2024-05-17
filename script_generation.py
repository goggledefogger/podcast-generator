import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script(topic, num_speakers, duration):
    prompt = f"Generate a {duration} minute podcast script with {num_speakers} speakers discussing the topic: {topic}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use a chat completion model
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates podcast scripts."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7,
    )

    script = response.choices[0].message['content'].strip()
    return script
