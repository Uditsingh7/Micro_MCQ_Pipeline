# run.py

from app.pipeline import generate_mcq

if __name__ == '__main__':
    user_input = {
        "context": "Explain the process of Photosynthesis and Light Reactions",
        "user_profile": {
            "role": "Student",
            "academic_level": "Class 11",
            "years_of_experience": 0,
            "learning_goal": "Master the basics for NEET exam",
            "exam_style": "NEET",
            "preferred_question_type": "Conceptual",
            "difficulty_level": "Intermediate"
        }
    }

    result = generate_mcq(user_input["context"], user_input["user_profile"])
    print("\n===== FINAL OUTPUT =====\n")
    print(result)
