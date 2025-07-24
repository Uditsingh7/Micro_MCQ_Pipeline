# prompts.py

def create_stage1_prompt(input_context):
    stage1_prompt = f"""##Instructions##
Given the context, focus on a meaningful topic and explain it clearly.
This explanation will later be used to generate high quality questions.

##context## : {input_context}
##Your Explanation## :
"""
    return stage1_prompt


def create_stage2_prompt(explanation, template, role, years_of_experience, selected_difficulty, evaluator_context=None):
    if not evaluator_context:
        IO_Prompt = f"""##Instruction##
Based on the explanation provided, generate a high-quality {template}-style question that can later be converted into an MCQ.
Avoid revealing the exact solution in the question statement.

### Explanation ###
{explanation}

### Candidate Parameters ###
Role: {role}
Experience: {years_of_experience} years
Difficulty: {selected_difficulty}

## Expected Output ##
Question:
Solution:
Correct Answer:
"""
    else:
        IO_Prompt = f"""##Instruction##
Based on the explanation provided, generate an improved high-quality {template}-style question for MCQ conversion.
Avoid revealing the exact solution in the question statement.
Also, use the evaluator_context below to fix any mistakes from the previous version.

### Explanation ###
{explanation}

### Candidate Parameters ###
Role: {role}
Experience: {years_of_experience} years
Difficulty: {selected_difficulty}
Evaluator Feedback: {evaluator_context}

## Expected Output ##
Question:
Solution:
Correct Answer:
"""
    return IO_Prompt

def create_stage3_prompt(explanation, question_answer, evaluator_context=None):
    if evaluator_context:
        IO_Prompt = f"""##Instruction##
You are provided with a concept explanation and a previously generated question-answer pair.

Your task:
- Create 3 strong distractor options based on common misconceptions or confusion points in the topic.
- The options should be realistic, not obviously wrong, and should challenge the candidate.
- Include a short explanation of why the correct answer is correct.
- Use the evaluator_context to improve on previous mistakes.

### Concept Explanation ###
{explanation}

### QA Pair ###
{question_answer}

### Evaluator Feedback ###
{evaluator_context}

## Expected Output ##
Question: ...
Options:
A) ...
B) ...
C) ...
D) ...  ← correct answer
Explanation: ...
"""
    else:
        IO_Prompt = f"""##Instruction##
You are provided with a concept explanation and a previously generated question-answer pair.

Your task:
- Create 3 strong distractor options based on common misconceptions or confusion points in the topic.
- The options should be realistic, not obviously wrong, and should challenge the candidate.
- Include a short explanation of why the correct answer is correct.

### Concept Explanation ###
{explanation}

### QA Pair ###
{question_answer}

## Expected Output ##
Question: ...
Options:
A) ...
B) ...
C) ...
D) ...  ← correct answer
Explanation: ...
"""
    return IO_Prompt


def stage4_formatting_prompt(raw_output: str) -> str:
    return (
        "You are a formatter."
        "Your task is to extract a valid JSON from the given MCQ content. Follow this structure exactly:"
        "{\n"
        "  \"question\": \"...\",\n"
        "  \"solution\": \"...\",\n"
        "  \"options\": [\n"
        "    \"Distractor 1\",\n"
        "    \"Distractor 2\",\n"
        "    \"Correct Answer\"\n"
        "  ],\n"
        "  \"explanation\": \"...\"\n"
        "}\n"
        "Make sure the correct answer is the LAST element in the options list."
        "Only return valid JSON and nothing else. Do not include commentary or formatting.\n\n"
        f"Input:\n{raw_output}"
    )

