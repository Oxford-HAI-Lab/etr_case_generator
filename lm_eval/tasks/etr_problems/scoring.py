import json
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
        answer_text = answer.get("text", "")
    elif isinstance(answer, list) and len(answer) > 0:
        answer_text = str(answer[0])
    else:
        answer_text = str(answer)

    # Find YES/NO in the response
    match = re.search(r"\b(YES|NO)\b", answer_text.upper())
    if not match:
        return {
            "correct": 0.0,
            "etr_agreement": 0.0,
            "etr_is_same_as_correct": 0.0,
            "correct_and_etr_agreement": 0.0,
            "correct_and_etr_disagreement": 0.0,
            "incorrect_and_etr_agreement": 0.0,
            "incorrect_and_etr_disagreement": 0.0,
            "len_response": len(answer_text),
            "parse_error": 1.0,
        }

    # print(json.dumps(question, indent=4))

    model_answer = match.group(1)
    is_conclusion_logically_correct: bool = question["scoring_guide"]["yes_no"]["conclusion_is_classically_correct"]
    conclusion_is_etr_predicted: bool = question["scoring_guide"]["yes_no"]["conclusion_is_etr_predicted"]

    logically_correct_str = "yes" if is_conclusion_logically_correct else "no"
    etr_predicted_str = "yes" if conclusion_is_etr_predicted else "no"

    etr_is_same_as_correct = is_conclusion_logically_correct == conclusion_is_etr_predicted

    print(f"Got model answer: {model_answer.lower()}\tCorrect answer: {logically_correct_str.lower()}\tETR answer: {etr_predicted_str.lower()}")

    # Calculate base metrics
    is_correct = model_answer.lower() == logically_correct_str.lower()
    agrees_with_etr = model_answer.lower() == etr_predicted_str.lower()
    
    # Calculate 2x2 matrix metrics
    correct_and_etr_agreement = float(is_correct and agrees_with_etr)
    correct_and_etr_disagreement = float(is_correct and not agrees_with_etr)
    incorrect_and_etr_agreement = float(not is_correct and agrees_with_etr)
    incorrect_and_etr_disagreement = float(not is_correct and not agrees_with_etr)
    
    return {
        "correct": float(is_correct),
        "etr_agreement": float(agrees_with_etr),
        "etr_is_same_as_correct": float(etr_is_same_as_correct),
        "correct_and_etr_agreement": correct_and_etr_agreement,
        "correct_and_etr_disagreement": correct_and_etr_disagreement,
        "incorrect_and_etr_agreement": incorrect_and_etr_agreement,
        "incorrect_and_etr_disagreement": incorrect_and_etr_disagreement,
        "len_response": len(answer_text),
        "parse_error": 0.0,
    }
