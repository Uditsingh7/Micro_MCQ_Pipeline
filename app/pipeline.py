# pipeline.py

import ast
from app.prompts import (
    create_stage1_prompt,
    create_stage2_prompt,
    create_stage3_prompt,
    stage4_formatting_prompt
)
from app.runpod_agent import query_llm
from app.evaluator import evaluate_mcq
from utils.json_extractor import extract_json
from utils.logger import logger
from utils.formatter import structure_mcq_output


def generate_mcq(context, user_profile):
    role = user_profile.get("role")
    years_of_experience = user_profile.get("years_of_experience")
    difficulty = user_profile.get("difficulty_level")
    model = "runpod-llm"

    # Stage 1: Explanation
    logger.info("Stage 1: Generating explanation...")
    stage1_prompt = create_stage1_prompt(context)
    explanation = query_llm(stage1_prompt, model, temperature=0.7)
    if explanation is None:
        return {"error": "Failed to get explanation."}

    # Stage 2: Question + Correct Answer
    logger.info("Stage 2: Generating question and answer...")
    stage2_prompt = create_stage2_prompt(
        explanation, template="scenario", role=role,
        years_of_experience=years_of_experience,
        selected_difficulty=difficulty
    )
    question_answer = query_llm(stage2_prompt, model, temperature=0.3)
    if question_answer is None:
        return {"error": "Failed to generate question and answer."}

    # Stage 3: Full MCQ (options + explanation)
    logger.info("Stage 3: Generating options and explanation...")
    stage3_prompt = create_stage3_prompt(explanation, question_answer)
    generator_response = query_llm(stage3_prompt, model, temperature=0.3)
    if generator_response is None:
        return {"error": "Failed to generate options and explanation."}

    # Attempt to extract the result
    question_data = extract_json(generator_response)

    # 🔽 Flatten Runpod nested format if needed
    if isinstance(question_data, list) and "choices" in question_data[0]:
        question_data = question_data[0]["choices"][0]["tokens"][0]
        try:
            question_data = ast.literal_eval(question_data)
        except Exception as e:
            logger.warning("Failed to parse response via literal_eval. Returning raw string.")
            question_data = {"raw_output": question_data}

    loop_threshold = 3
    loop_count = 0

    while loop_count < loop_threshold:
        logger.info("Stage 4: Evaluation round %d", loop_count + 1)
        feedback, decision = evaluate_mcq(generator_response)

        if decision in ["question", "solution"]:
            logger.info("Decision: %s. Regenerating question and options...", decision)
            stage2_prompt = create_stage2_prompt(
                explanation, template="scenario", role=role,
                years_of_experience=years_of_experience,
                selected_difficulty=difficulty,
                evaluator_context=str(feedback)
            )
            question_answer = query_llm(stage2_prompt, model, temperature=0.3)
            if question_answer is None:
                return {"error": "Failed to regenerate question."}

            stage3_prompt = create_stage3_prompt(explanation, question_answer)
            generator_response = query_llm(stage3_prompt, model, temperature=0.3)
            if generator_response is None:
                return {"error": "Failed to regenerate options."}

            question_data = extract_json(generator_response)

        elif decision == "options":
            logger.info("Decision: %s. Regenerating options only...", decision)
            stage3_prompt = create_stage3_prompt(explanation, question_answer, str(feedback))
            generator_response = query_llm(stage3_prompt, model, temperature=0.3)
            if generator_response is None:
                return {"error": "Failed to regenerate options."}
            question_data = extract_json(generator_response)

        else:
            logger.info("Decision: %s. No regeneration needed.", decision)
            break

        loop_count += 1

    return {
        "question": question_data,
        "evaluation": feedback,
        "revision_needed": decision
    }
