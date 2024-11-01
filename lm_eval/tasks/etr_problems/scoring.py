import re
import os
import sys

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())

def score_answer(question, answer):
    """
    Score the given answer based on correctness and explanation quality.
    """
    return {
        "correct": 0.0,
        "has_explanation": 0.0,
        "answer_present": 0.0,
        "len_response": 0
    }
