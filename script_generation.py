import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1") # Default to OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
client = OpenAI(base_url=LLM_BASE_URL, api_key=OPENAI_API_KEY)

def generate_script(topic, num_speakers, duration):
    prompt = f"Generate a {duration} minute podcast script with {num_speakers} speakers discussing the topic: {topic}"

    if LLM_BASE_URL == "https://api.openai.com/v1":
        logging.info("Using OpenAI API...")
        # Use the OpenAI API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates podcast scripts."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo",
            max_tokens=3000,
            temperature=0.7,
        )
        script = chat_completion.choices[0].message.content.strip()

    else:
        logging.info("Using local LLM endpoint...")
        # Use your local LLM endpoint
        completion = client.chat.completions.create(
          model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
          messages=[
            {"role": "system", "content": "Always answer in rhymes."},
            {"role": "user", "content": "Introduce yourself."}
          ],
          temperature=0.7,
        )

        script = completion.choices[0].message

    return script
