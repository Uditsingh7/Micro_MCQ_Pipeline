# utils/types.py

from typing import TypedDict, List

class MCQ(TypedDict):
    Question: str
    Correct_Answer: str
    Solution: str
    Option_1: str
    Option_2: str
    Option_3: str
