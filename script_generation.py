import os
import logging
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")  # Default to OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
client = OpenAI(base_url=LLM_BASE_URL, api_key=OPENAI_API_KEY)

# Load the system prompt and user prompt template from llm_config.json
with open('llm_config.json', 'r') as config_file:
    llm_config = json.load(config_file)

SYSTEM_PROMPT = llm_config.get("system_prompt", "You are a helpful assistant that generates podcast scripts. When responding, return only the script content without any introductions, explanations, timestamps, or additional formatting. The number of speakers provided should be exactly the number of people in the podcast, including hosts and guests. Ensure that each speaker's name is used consistently throughout the script.")
USER_PROMPT_TEMPLATE = llm_config.get("user_prompt_template", "Generate a {duration} minute podcast script with {num_speakers} speaker{plural} discussing the topic: {topic}. Ensure there are exactly {num_speakers} speaker{plural}, and use the names {speakers} consistently throughout the script. Do not include any timestamps or additional formatting.")

def generate_script(topic, num_speakers, duration):
    speakers = ["Speaker 1"] if num_speakers == 1 else [f"Speaker {i+1}" for i in range(num_speakers)]
    plural = 's' if num_speakers > 1 else ''
    speakers_list = ' and '.join(speakers)
    prompt = USER_PROMPT_TEMPLATE.format(duration=duration, num_speakers=num_speakers, plural=plural, topic=topic, speakers=speakers_list)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    if LLM_BASE_URL == "https://api.openai.com/v1":
        logging.info("Using OpenAI API...")
        # Use the OpenAI API
        chat_completion = client.chat.completions.create(
            messages=messages,
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
            messages=messages,
            temperature=0.7,
        )

        script = completion.choices[0].message.content.strip()

    return script
