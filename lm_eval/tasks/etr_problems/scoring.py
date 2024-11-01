import re
import os
import sys

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())

def score_answer(question, answer):
    """
    Score the given answer based on whether it correctly identifies if the conclusion follows.
    
    Args:
        question (dict): A dictionary containing the question and scoring guide
        answer (str or dict): The model's response to the ETR question
        
    Returns:
        dict: A dictionary containing the score and response length
    """
    # Extract answer text
    if isinstance(answer, dict):
        answer_text = answer.get('text', '')
    elif isinstance(answer, list) and len(answer) > 0:
        answer_text = str(answer[0])
    else:
        answer_text = str(answer)

    # Find YES/NO in the response
    match = re.search(r'\b(YES|NO)\b', answer_text.upper())
    if not match:
        return {
            "correct": 0.0,
            "len_response": len(answer_text)
        }
    
    model_answer = match.group(1)
    correct_answer = question['scoring_guide']['answer']
    
    return {
        "correct": float(model_answer == correct_answer),
        "len_response": len(answer_text)
    }
