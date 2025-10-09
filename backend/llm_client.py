import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file in development.
load_dotenv()

# Configure provider via env:
LLM_MODE = os.getenv("LLM_MODE", "mock")  
# "mock" => returns canned text (useful for frontend dev)
# "http" => POST to an external endpoint specified by LLM_ENDPOINT and LLM_API_KEY

LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")  # e.g. https://api.example-llm.com/analyze
LLM_API_KEY = os.getenv("LLM_API_KEY")    # provider API key (optional)

PROMPT_TEMPLATE = os.getenv(
    "PROMPT_TEMPLATE",
    "Here is a screenshot of the current application. The task description is: '{task}'. "
    "Based on the screenshot, what should the user press or do next to accomplish the task? "
    "Be concise and list the single most likely next action followed by a short rationale."
)

def call_provider(image_bytes: bytes, task: str):
    """
    Provider-agnostic wrapper.
    Returns (success_bool, reply_or_error_string).
    """
    if LLM_MODE == "mock":
        # quick fake reply for testing
        logging.info("LLM_MODE=mock -> returning canned reply")
        return True, f"(mock reply) For task: '{task}' - Try clicking the top-right button labeled 'Next'."

    if LLM_MODE == "http":
        if not LLM_ENDPOINT:
            return False, "LLM_ENDPOINT not configured in environment."

        # Build the prompt using the template above
        prompt = PROMPT_TEMPLATE.format(task=task)
        headers = {}
        if LLM_API_KEY:
            headers["Authorization"] = f"Bearer {LLM_API_KEY}"

        # This example sends the image as multipart/form-data along with prompt.
        # Adapt this function to match the provider API.
        files = {"image": ("screenshot.png", image_bytes, "image/png")}
        data = {"prompt": prompt}

        try:
            resp = requests.post(LLM_ENDPOINT, files=files, data=data, headers=headers, timeout=60)
            resp.raise_for_status()

            # Expect provider to return JSON.
            j = resp.json()
            for key in ("reply", "response", "answer", "text"):
                if key in j:
                    return True, j[key]
            # Fallback: return entire JSON string
            return True, str(j)
        except Exception as e:
            return False, str(e)

    return False, f"Unknown LLM_MODE='{LLM_MODE}'"