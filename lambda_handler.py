# lambda_handler.py
import json
import os
from app.pipeline import generate_mcq
from utils.logger import logger

def _response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }

def lambda_handler(event, context):
    try:
        # Support both direct invocation and API Gateway proxy events
        if isinstance(event, dict) and "body" in event and event.get("isBase64Encoded") in (True, False):
            # API Gateway proxy integration
            raw_body = event.get("body")
            if event.get("isBase64Encoded"):
                import base64
                raw_body = base64.b64decode(raw_body).decode("utf-8")
            payload = json.loads(raw_body) if raw_body else {}
        else:
            # Direct invoke with plain JSON event
            payload = event or {}

        context_text = payload.get("context")
        user_profile = payload.get("user_profile")

        if not context_text or not isinstance(user_profile, dict):
            return _response(400, {"error": "Invalid input. Expected { 'context': str, 'user_profile': dict }"})

        logger.info("Invoking generate_mcq with provided context and profile")
        result = generate_mcq(context_text, user_profile)

        # Normalize output to dict
        if isinstance(result, str):
            body = {"result": result}
        elif isinstance(result, dict):
            body = result
        else:
            body = {"result": str(result)}

        return _response(200, body)

    except Exception as e:
        logger.exception("Lambda handler error")
        return _response(500, {"error": f"Internal error: {str(e)}"})
