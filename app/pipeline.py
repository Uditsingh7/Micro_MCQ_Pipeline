# pipeline.py

import ast
import json
import re
from app.prompts import (
    create_stage1_prompt,
    create_stage2_prompt,
    create_stage3_prompt
)
from app.runpod_agent import query_llm
from app.evaluator import evaluator_agent
from utils.json_extractor import extract_json 
from utils.logger import logger
from app.continuity_agent import decide_revision_action


def generate_mcq(context, user_profile):
    role = user_profile.get("role")
    years_of_experience = user_profile.get("years_of_experience")
    difficulty = user_profile.get("difficulty_level")
    model = "runpod-llm"

    try:
        # Stage 1: Explanation
        logger.info("🔵 Stage 1: Generating explanation...")
        stage1_prompt = create_stage1_prompt(context)
        explanation = query_llm(stage1_prompt, model, temperature=0.7)
        explanation = explanation[0]['choices'][0]['tokens'][0]
        explanation = re.sub(r"<think>.*?</think>", "", explanation, flags=re.DOTALL)

        if not explanation:
            return {"error": "Failed to generate explanation."}
        logger.info("Explanation: %s", explanation)

        # Stage 2: Question + Correct Answer
        logger.info("🟢 Stage 2: Generating question and answer...")
        stage2_prompt = create_stage2_prompt(
            explanation, template="scenario", role=role,
            years_of_experience=years_of_experience,
            selected_difficulty=difficulty
        )
        logger.info("Stage 2 Prompt: %s", stage2_prompt)
        question_answer = query_llm(stage2_prompt, model, temperature=0.7)
        question_answer = question_answer[0]['choices'][0]['tokens'][0]
        question_answer = re.sub(r"<think>.*?</think>", "", question_answer, flags=re.DOTALL)
        question_answer = re.sub(r"</?raw>", "", question_answer, flags=re.DOTALL)
        if not question_answer:
            return {"error": "Failed to generate question and answer."}
        logger.info("Question and Answer: %s", question_answer)

        # Stage 3: Full MCQ (options + explanation)
        logger.info("🟣 Stage 3: Generating full MCQ...")
        stage3_prompt = create_stage3_prompt(explanation, question_answer)
        logger.info("Stage 3 Prompt: %s", stage3_prompt)
        generator_response = query_llm(stage3_prompt, model, temperature=0.7)
        generator_response = generator_response[0]['choices'][0]['tokens'][0]
        generator_response = re.sub(r"<think>.*?</think>", "", generator_response, flags=re.DOTALL)
        generator_response = re.sub(r"</?raw>", "", generator_response, flags=re.DOTALL)
        if not generator_response:
            return {"error": "Failed to generate MCQ options."}
        # logger.info("Initial MCQ: %s", generator_response)

        # Evaluation + Regeneration Loop
        loop_count = 0
        loop_threshold = 3
        while loop_count < loop_threshold:
            logger.info("🔍 Evaluation Round %d", loop_count + 1)
            evaluator_feedback, token = evaluator_agent(generator_response)
            
            decision = decide_revision_action(
            evaluator_feedback=json.dumps(evaluator_feedback, indent=2),
            generator_response=generator_response,
            model=model
            )
            
            logger.info("Evaluator Feedback: %s", evaluator_feedback)
            logger.info("Decision: %s", decision)


            if decision in ["question", "solution"]:
                logger.info("🔁 Regenerating question/solution due to: %s", decision)
                stage2_prompt = create_stage2_prompt(
                    explanation, template="scenario", role=role,
                    years_of_experience=years_of_experience,
                    selected_difficulty=difficulty,
                    evaluator_context=evaluator_feedback
                )
                question_answer = query_llm(stage2_prompt, model, temperature=0.3)
                question_answer = question_answer[0]['choices'][0]['tokens'][0]
                question_answer = re.sub(r"<think>.*?</think>", "", question_answer, flags=re.DOTALL)
                question_answer = re.sub(r"</?raw>", "", question_answer, flags=re.DOTALL)
                if not question_answer:
                    return {"error": "Failed to regenerate question and answer."}

                stage3_prompt = create_stage3_prompt(explanation, question_answer)
                generator_response = query_llm(stage3_prompt, model, temperature=0.3)
                generator_response = re.sub(r"<think>.*?</think>", "", generator_response, flags=re.DOTALL)
                generator_response = re.sub(r"</?raw>", "", generator_response, flags=re.DOTALL)
                if not generator_response:
                    return {"error": "Failed to regenerate MCQ options."}

            elif decision == "options":
                logger.info("🔁 Regenerating options due to: %s", decision) 
                stage3_prompt = create_stage3_prompt(
                    explanation, question_answer, evaluator_feedback
                )
                generator_response = query_llm(stage3_prompt, model, temperature=0.3)
                generator_response = generator_response[0]['choices'][0]['tokens'][0]
                generator_response = re.sub(r"<think>.*?</think>", "", generator_response, flags=re.DOTALL)
                generator_response = re.sub(r"</?raw>", "", generator_response, flags=re.DOTALL)
                if not generator_response:
                    return {"error": "Failed to regenerate MCQ options."}

            else:
                logger.info("✅ Evaluation passed. No regeneration needed.")
                break

            loop_count += 1

        return generator_response

    except Exception as e:
        logger.exception("❌ Exception in generate_mcq:")
        return {"error": f"Unexpected error during MCQ generation: {str(e)}"}
