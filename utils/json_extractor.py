import ast
import re

def extract_json(raw_text):
    if isinstance(raw_text, (dict, list)):
        return raw_text  # already parsed

    try:
        return ast.literal_eval(raw_text)
    except Exception:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return ast.literal_eval(match.group())
        raise
