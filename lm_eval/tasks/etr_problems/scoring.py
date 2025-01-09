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
        return {"correct": 0.0, "len_response": len(answer_text)}

    # print(json.dumps(question, indent=4))

    model_answer = match.group(1)
    is_conclusion_logically_correct: bool = question["scoring_guide"]["yes_no"]["conclusion_is_classically_correct"]
    conclusion_is_etr_predicted: bool = question["scoring_guide"]["yes_no"]["conclusion_is_etr_predicted"]

    logically_correct_str = "yes" if is_conclusion_logically_correct else "no"
    etr_predicted_str = "yes" if conclusion_is_etr_predicted else "no"

    print(f"Got model answer: {model_answer.lower()}\tCorrect answer: {logically_correct_str.lower()}\tETR answer: {etr_predicted_str.lower()}")

    return {
        "correct": float(model_answer.lower() == logically_correct_str.lower()),
        "etr_agreement": float(model_answer.lower() == etr_predicted_str.lower()),
        "len_response": len(answer_text),
    }
