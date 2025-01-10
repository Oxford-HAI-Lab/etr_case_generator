import json
import re
import os
import sys

from pyetr import View
from pysmt.fnode import FNode
from etr_case_generator.generator2.formatting_smt import load_fnode_from_string
from etr_case_generator.generator2.logic_helper import does_it_follow
from pyetr.inference import default_procedure_does_it_follow
from smt_interface.smt_encoder import view_to_smt

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

    print(json.dumps(question, indent=4))

    # Find "The following follows" in the answer_text, and get the substring after it
    model_answer = None
    match = re.search(r"(?<=following follows: )(.*)", answer_text)
    if not match:
        match = re.search(r"(?<=Answer: )(.*)", answer_text)
    # Find a matching pair of curly brackets in the answer_text
    if not match:
        match = re.search(r"\{([^}]+)\}", answer_text)
        model_answer = match.group(1) if match else None

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
        # TODO This fails too often!
        print(f"Could not find a match in this answer: {answer_text}")
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

    # Try to see if it follows!
    model_view_etr = View.from_str(model_answer)
    model_view_smt_fnode = view_to_smt(model_view_etr)
    premises = question["scoring_guide"]["generation_details"]["premises"]
    premises_view = [View.from_str(p) for p in premises]
    premises_fnodes = [view_to_smt(v) for v in premises_view]
    is_classically_correct: bool = does_it_follow(premises_fnodes, model_view_smt_fnode)
    is_etr_predicted: bool = default_procedure_does_it_follow(premises_view, model_view_etr)

    print(f"ETR predicted: {is_etr_predicted}")
    print(f"Classically correct: {is_classically_correct}")


    # correct_answer = question["scoring_guide"]["logically_correct_answer"]
    # # print(f"Correct answer: {correct_answer}")  # This will be "YES" or "NO", which doesn't help us here
    #
    # etr_answer = question["scoring_guide"]["etr_conclusion"][0]
    # print(f"ETR conclusion: {etr_answer}")
    #
    # # Get premises
    # premises = [p[0] for p in question["scoring_guide"]["premises"]]
    # print(f"Premises: {premises}")
    #
    # # TODO Need to call does_it_follow
    #
    # # Let's check if the model answer is contained within the ETR answer
    # # First, get only the contents insider the curly brackets of the model answer
    # model_match = re.search(r"\{(.*)\}", model_answer)
    # etr_match = re.search(r"\{(.*)\}", etr_answer)
    #
    # if model_match and etr_match:
    #     model_answer_contents = model_match.group(1)
    #     etr_answer_contents = etr_match.group(1)
    #     kinda_same = model_answer_contents in etr_answer_contents
    # else:
    #     kinda_same = False

    return {
        "correct": float(is_classically_correct),
        "etr_predicted": float(is_etr_predicted),
        "len_response": len(answer_text),
    }
