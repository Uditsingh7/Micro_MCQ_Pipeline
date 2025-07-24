# run.py

from app.pipeline import generate_mcq

if __name__ == '__main__':
    user_input = {
  "context": "Explain the concept of word embeddings in NLP",
  "user_profile": {
    "role": "machine learning engineer",
    "years_of_experience": 3,
    "difficulty_level": "Advanced"
  }
}

    result = generate_mcq(user_input["context"], user_input["user_profile"])
    print("\n===== FINAL OUTPUT =====\n")
    print(result)
