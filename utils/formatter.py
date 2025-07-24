import re

def structure_mcq_output(raw_text):
    """
    Parse raw model response and extract:
    - question
    - correct answer
    - solution
    - options
    - explanation
    """

    def extract_field(name):
        pattern = rf'{name}:\s*"(.*?)"'
        match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else f"{name} not found"

    question = extract_field("question")
    solution = extract_field("solution")
    explanation = extract_field("explanation")

    options = []
    for i in range(1, 5):
        opt = extract_field(f"option {i}")
        if "not found" not in opt.lower():
            options.append(opt)

    if not options:
        options = ["Option parsing failed"]

    return {
        "question": question,
        "solution": solution,
        "options": options,
        "explanation": explanation
    }
