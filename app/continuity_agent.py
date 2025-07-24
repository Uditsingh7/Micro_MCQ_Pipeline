import re
from app.prompts import CONTINUITY_DECISION_PROMPT
from app.runpod_agent import query_llm
from utils.logger import logger

def decide_revision_action(evaluator_feedback: str, generator_response: str, model="default_thinking_model") -> str:
    """
    Uses evaluator feedback and original MCQ to decide what (if anything) needs revision.
    Returns one of: "question", "solution", "options", "none"
    """
    prompt = CONTINUITY_DECISION_PROMPT.format(
        evaluator_feedback=evaluator_feedback.strip(),
        generator_output=generator_response.strip()
    )
    
    response = query_llm(prompt, model=model, temperature=0.3)
    response = response[0]['choices'][0]['tokens'][0]
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
    response = re.sub(r"</?raw>", "", response, flags=re.DOTALL)
    logger.info("Decision Response: %s", response)
    
    # Expected response: {"Decision": "question"}
    match = re.search(r'"?Decision"?\s*:\s*"?(\w+)"?', response)
    if match:
        return match.group(1).lower()
    return "none"
