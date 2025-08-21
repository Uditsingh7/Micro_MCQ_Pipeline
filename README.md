# MCQ Microlearning Generator — Agentic Workflow

Welcome! This project generates high‑quality multiple‑choice questions (MCQs) for microlearning, using a staged “agentic” workflow and an automated evaluator loop. It’s designed to be practical, easy to run locally, and ready to deploy to serverless (AWS Lambda) when needed.

## What this project does (business-first)

- Creates exam‑style MCQs (or non‑MCQ questions) from a topic, chapter extract, or document.
- Adapts to learner profile: grade/level, exam style (e.g., NEET/JEE), difficulty.
- Improves item quality automatically via an evaluator loop that gives targeted feedback and refines only what’s needed (question, solution, or options).
- Outputs clean, ready‑to‑use quiz items for a microlearning app.

Think of it as a question-generation funnel:

1) Ground the concept → 2) Draft question + solution → 3) Compose options (if MCQ) → 4) Evaluate and refine → 5) Finalize and deliver.

## How the funnel works (behavioral flow)

- Stage 1: Concept grounding
    - Distills the input topic into a concise, factual explanation to anchor all later steps.
- Stage 2: Question + solution
    - Generates a profile‑aware question and its solution/answer, guided by Stage 1.
- Stage 3: MCQ options
    - Composes strong distractors and a correct option, using Stages 1 and 2 for consistency.
- Evaluator loop (automated QA)
    - Checks clarity, correctness, and option distinctiveness.
    - Decides minimal fix scope: regenerate “question/solution” (Stage 2), “options” (Stage 3), or accept.
    - Iterates up to a small cap for faster convergence and lower cost.
- Finalization
    - Returns a clean item payload (MCQ or non‑MCQ) for delivery.


## Architecture overview (tech perspective)

- Orchestrator: Coordinates stages, passes artifacts between prompts, manages the evaluation loop.
- Prompt stages: Three simple, single‑responsibility prompts (concept → Q+A → MCQ options).
- Evaluator + decision: LLM‑based rubric checks produce structured feedback; a decision component maps feedback to the smallest regeneration needed.
- LLM access: A thin gateway function handles outbound calls, timeouts, and error handling.
- No persistent storage (current setup): Everything is in-memory per request; easy to add DB later if needed.


### Diagram (Mermaid)
![MCQ Microlearning Generator — Agentic Workflow](https://github.com/Uditsingh7/public-media-store/blob/main/micro_learniing_agent_steps_diagram%20_%20Mermaid%20Chart-2025-08-19-063544.png)
## Key design principles

- Separation of concerns: Each stage has one job; evaluator is isolated as a quality gate.
- Grounded generation: Stage 1 explanation reduces ambiguity and stabilizes downstream outputs.
- Minimal regeneration: Only fix what’s broken (options vs. question/solution) to save time and cost.
- Determinism where it matters: Lower temperature on refinement passes for convergence.
- Extensibility: Easy to swap LLMs, add new item types, or plug in storage/analytics later.


## Inputs and outputs (what to send, what you get)

- Input
    - context: topic text or cleaned content extracted from documents
    - user_profile: role, academic_level, exam_style, difficulty_level, preferred_question_type

Example user_profile fields:

- role: Student
- academic_level: Class 11
- exam_style: NEET
- preferred_question_type: mcq
- difficulty_level: Intermediate
- Output
    - For MCQ: question, options A–D, correct answer, explanation
    - For non‑MCQ: question, solution, answer


## Running locally (quick start)

1) Prerequisites

- Python 3.10+ (3.11 recommended)
- A terminal and internet access (to reach the LLM endpoint)
- A RunPod (or equivalent) endpoint and API key

2) Clone and set up

- Create a virtual environment:
    - python -m venv .venv
    - source .venv/bin/activate  (Linux/Mac)
    - .venv\Scripts\activate     (Windows)
- Install dependencies:
    - pip install -r requirements.txt

3) Environment variables

- Export environment variables (replace with your values):
    - RUNPOD_API_KEY=your_key_here
    - RUNPOD_ENDPOINT=https://api.runpod.ai/your-endpoint
- You can use a .env file for local development; the code will read from the environment. In production (Lambda), set env vars in the function configuration.

4) Run from the CLI

- The simplest way:
    - python run.py
- Or import and call generate_mcq in a script/notebook:
    - from app.pipeline import generate_mcq
    - result = generate_mcq(context_text, user_profile_dict)
    - print(result)

Tips

- Start with a short, focused context (e.g., a paragraph about a concept).
- Adjust difficulty and exam_style in user_profile to see how the output adapts.


## Project structure (high-level)

- app/
    - pipeline.py: Orchestrates stages and evaluation loop
    - prompts.py: Prompt builders for stages 1–3
    - evaluator.py: LLM‑based evaluation logic
    - runpod_agent.py: Outbound LLM calls with timeouts/error handling
- utils/
    - logger.py: Simple, Lambda‑friendly logging
- run.py: Local entry to run the pipeline
- lambda_handler.py: Serverless entrypoint (for AWS Lambda/SAM)
- requirements.txt: Dependencies


## Error handling and quality

- Timeouts: Network calls use timeouts to avoid hanging. Adjust as needed.
- Exceptions: Errors are logged and surfaced as clear messages (and JSON in Lambda mode).
- Evaluator loop: Caps iterations to prevent runaway costs and long latencies.


## Deploying to AWS Lambda (short summary)

- Lambda handler: lambda_handler.py expects an event with “context” and “user_profile”.
- SAM template: template.yaml defines the function (runtime, handler, memory/timeout).
- Build and deploy:
    - sam build
    - sam deploy --guided
- Set RUNPOD_API_KEY and RUNPOD_ENDPOINT during deploy.
- Test with a JSON event in the AWS Console or sam local invoke.

If you only want local execution, you can ignore Lambda and just run run.py.

## Roadmap (optional enhancements)

- Storage: Persist finalized items, logs, and intermediate artifacts (e.g., Postgres + S3).
- Observability: Centralized metrics (latency, pass rate) and tracing for production.
- Model routing: LLM choice per stage (cost/accuracy/latency‑aware).
- Policy/config: Central place to tweak temperatures, max loops, and prompt variants.
- Bulk generation: Batch processing for chapters or curricula.


## FAQs

- Does it support non‑MCQ outputs?
    - Yes. Stage 3 (options) is conditional; non‑MCQ stops after Stage 2 and still passes through evaluation.
- Can I use a different LLM provider?
    - Yes. The gateway is thin; replace the endpoint and auth as needed.
- How do I integrate with a frontend app?
    - Wrap the pipeline in an API (e.g., FastAPI or API Gateway + Lambda). The output is already a clean JSON bundle suitable for UI rendering.
- How do I keep costs under control?
    - Use short contexts, cap evaluator iterations, and cache repeated topics if you add storage later.


## Contributing

- Keep prompts modular and declarative.
- Ensure handler outputs are always JSON‑serializable.
- Add tests for evaluator decisions when changing rubrics or prompt wording.





