import logging
from llm_utils import call_llm, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

def generate_script(topic, num_speakers, duration):
    speakers = ["Speaker 1"] if num_speakers == 1 else [f"Speaker {i+1}" for i in range(num_speakers)]
    plural = 's' if num_speakers > 1 else ''
    speakers_list = ' and '.join(speakers)
    prompt = USER_PROMPT_TEMPLATE.format(duration=duration, num_speakers=num_speakers, plural=plural, topic=topic, speakers=speakers_list)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    script = call_llm(messages)
    return script
