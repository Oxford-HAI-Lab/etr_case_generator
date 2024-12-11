import re
import os
import sys

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())


def score_answer(question, model_answer):
    """
    Score the given answer based on whether it correctly identifies if the conclusion follows.

    Args:
        question (dict): A dictionary containing the question and scoring guide
        model_answer (str or dict): The model's response to the ETR question

    Returns:
        dict: A dictionary containing the score and response length
    """
    # Extract answer text
    if isinstance(model_answer, dict):
        answer_text = model_answer.get("text", "")
    elif isinstance(model_answer, list) and len(model_answer) > 0:
        answer_text = str(model_answer[0])
    else:
        answer_text = str(model_answer)

    print(f"Got this answer text: {answer_text}")

    # Find "The following follows" in the answer_text, and get the substring after it
    model_answer = None
    match = re.search(r"(?<=following follows: )(.*)", answer_text)
    if match:
        model_answer = match.group(1)
    if not model_answer:
        # Find the second to last instance of "`" in the answer_text
        match = re.search(r"`([^`]+)`[^`]*$", answer_text)
        model_answer = match.group(1) if match else None
    if not model_answer:
        # Try to just find "follows" or "Follows" in the response, case insensitive and fairly generous
        match = re.search(r"(?i)(?:follows|follows:|follows :|follows,|follows, :)(.*)", answer_text)
        model_answer = match.group(1) if match else None

    if not model_answer:
        return {"correct": 0.0, "len_response": len(answer_text)}
    else:
        print(f"Matched this answer: {model_answer}")

    # Let's try to clean up the answer
    # Remove "`." from the end of the answer (but not anywhere else in the string)
    model_answer = model_answer.strip()
    model_answer = re.sub(r"^:", "", model_answer)
    model_answer = re.sub(r"`\.$", "", model_answer)
    model_answer = re.sub(r"`$", "", model_answer)
    model_answer = re.sub(r"\.$", "", model_answer)
    model_answer = re.sub(r"^`", "", model_answer)

    print(f"Matched and parsed: {model_answer}")

    correct_answer = question["scoring_guide"]["logically_correct_answer"]
    # print(f"Correct answer: {correct_answer}")  # This will be "YES" or "NO", which doesn't help us here

    etr_answer = question["scoring_guide"]["etr_conclusion"][0]
    print(f"ETR conclusion: {etr_answer}")

    # Get premises
    premises = [p[0] for p in question["scoring_guide"]["premises"]]
    print(f"Premises: {premises}")

    return {
        "correct": float(model_answer.lower() == correct_answer.lower()),
        "same_as_etr": float(model_answer.lower() == etr_answer.lower()),
        "len_response": len(answer_text),
    }
