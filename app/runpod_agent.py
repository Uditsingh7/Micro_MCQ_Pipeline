
import requests
import os
import logging
import json
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {RUNPOD_API_KEY}"
}
 
def query_llm(prompt: str, model: str = "runpod-llm", temperature: float = 0.7, max_tokens: int = 4096) -> str:
    if not RUNPOD_API_KEY or not RUNPOD_ENDPOINT:
        logger.error("Missing RUNPOD_API_KEY or RUNPOD_ENDPOINT in environment.")
        return None

    # Correct RunPod API format
    api_payload = {
        "input": {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "sampling_params": {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
    }

    try:
        logger.info("Querying Runpod model: %s", model)
        response = requests.post(RUNPOD_ENDPOINT, headers=HEADERS, json=api_payload)
        response.raise_for_status()
        response_json = response.json()

        if "output" not in response_json:
            logger.error("Runpod response missing 'output' field: %s", response_json)
            return None

        response_text = response_json["output"]
        return response_text

    except Exception as e:
        logger.exception("Runpod query failed: %s", str(e))
        return None
