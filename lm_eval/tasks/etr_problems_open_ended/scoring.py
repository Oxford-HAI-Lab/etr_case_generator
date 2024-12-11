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

    print(f"Got this answer text: {answer_text}")

    # Find "The following follows" in the answer_text, and get the substring after it
    match = re.search(r"(?<=The following follows: )(.*)", answer_text)
    if not match:
        return {"correct": 0.0, "len_response": len(answer_text)}
    else:
        print(f"Matched this: {match.group(1)}")

    # Find YES/NO in the response
    match = re.search(r"\b(YES|NO)\b", answer_text.upper())
    if not match:
        return {"correct": 0.0, "len_response": len(answer_text)}

    model_answer = match.group(1)
    correct_answer = question["scoring_guide"]["logically_correct_answer"]

    return {
        "correct": float(model_answer.lower() == correct_answer.lower()),
        "len_response": len(answer_text),
    }
