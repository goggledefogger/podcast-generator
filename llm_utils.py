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

SYSTEM_PROMPT = llm_config.get("system_prompt")
USER_PROMPT_TEMPLATE = llm_config.get("user_prompt_template")
FIELD_PROMPTS = llm_config.get("field_prompts")

def call_llm(messages):
    if LLM_BASE_URL == "https://api.openai.com/v1":
        logging.info("Using OpenAI API...")
        # Use the OpenAI API
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            max_tokens=3000,
            temperature=0.7,
        )
        response_content = chat_completion.choices[0].message.content.strip()
    else:
        logging.info("Using local LLM endpoint...")
        # Use your local LLM endpoint
        completion = client.chat.completions.create(
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            messages=messages,
            temperature=0.7,
        )
        response_content = completion.choices[0].message.content.strip()

    return response_content

def get_prompt(field, context):
    logging.info(f"Fetching prompt for field: {field}")
    categories = field.split('.')
    prompt = FIELD_PROMPTS
    for category in categories:
        logging.info(f"Accessing category: {category}")
        prompt = prompt.get(category, None)
        if prompt is None:
            logging.error(f"Prompt for category '{category}' not found.")
            return None
    if isinstance(prompt, str):
        logging.info(f"Prompt found: {prompt}")
        return prompt.format(**context)
    else:
        logging.error(f"Invalid prompt structure for field '{field}'.")
        return None

