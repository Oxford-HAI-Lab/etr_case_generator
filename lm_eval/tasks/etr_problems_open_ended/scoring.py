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
    answer = None
    match = re.search(r"(?<=following follows: )(.*)", answer_text)
    if match:
        answer = match.group(1)
    if not answer:
        # Find the second to last instance of "`" in the answer_text
        match = re.search(r"`([^`]+)`[^`]*$", answer_text)
        answer = match.group(1) if match else None
    if not answer:
        # Try to just find "follows" or "Follows" in the response, case insensitive and fairly generous
        match = re.search(r"(?i)(?:follows|follows:|follows :|follows,|follows, :)(.*)", answer_text)
        answer = match.group(1) if match else None

    if not answer:
        return {"correct": 0.0, "len_response": len(answer_text)}
    else:
        print(f"Matched this answer: {answer}")

    # Let's try to clean up the answer
    # Remove "`." from the end of the answer (but not anywhere else in the string)
    answer = answer.strip()
    answer = re.sub(r"^:", "", answer)
    answer = re.sub(r"`\.$", "", answer)
    answer = re.sub(r"`$", "", answer)
    answer = re.sub(r"\.$", "", answer)
    answer = re.sub(r"^`", "", answer)

    print(f"Matched and parsed: {answer}")

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
