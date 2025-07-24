# runpod_agent.py

import requests
import os
import logging
import json
from utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")  # e.g., "https://api.runpod.ai/v2/your-endpoint-id/run"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {RUNPOD_API_KEY}"
}

def query_llm(prompt: str, model: str = "runpod-llm", temperature:int = 0.7) -> str:
    if not RUNPOD_API_KEY or not RUNPOD_ENDPOINT:
        logger.error("Missing RUNPOD_API_KEY or RUNPOD_ENDPOINT in environment.")
        return None

    payload = {
        "input": {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": 4096
        }
    }
    try:
        logger.info("Querying Runpod model: %s", model)
        response = requests.post(RUNPOD_ENDPOINT, headers=HEADERS, json=payload)
        response.raise_for_status()
        response_json = response.json()

        if "output" not in response_json:
            logger.error("Runpod response missing 'output' field: %s", response_json)
            return None

        try:
            return response_json["output"]["choices"][0]["message"]["content"]
        except Exception:
            return str(response_json["output"])

    except Exception as e:
        logger.exception("Runpod query failed: %s", str(e))
        return None

