import json
import re
import os
import sys
import textwrap
import openai

from pyetr import View
from pysmt.fnode import FNode
from etr_case_generator.generator2.formatting_smt import load_fnode_from_string
from etr_case_generator.generator2.logic_helper import does_it_follow
from pyetr.inference import default_procedure_does_it_follow
from pyetr.inference import default_inference_procedure
from smt_interface.smt_encoder import view_to_smt

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())

# Set up openai client
openai.api_key = os.getenv("OPENAI_API_KEY")


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
    original_model_answer: str = answer_text
    print("-" * 80)
    print(f"Starting Open Ended Scoring. Got this answer text: {answer_text}")
    try:
        short_name_to_full_name: dict[str, str] = question["scoring_guide"]["open_ended"]["short_name_to_full_name"]
        num_attempts = 3
        for i in range(num_attempts):
            try:
                model_answer = use_model_get_etr_text(answer_text, short_name_to_full_name, temperature=0.2 + 0.2 * i)
                break
            except Exception as e:
                print(f"ETR Text Translation Failure {i}: {e}")
                if i == num_attempts - 1:
                    raise e
                continue

        print(f"Compare to predicted:", question["scoring_guide"]["etr_predicted"])

        # Try to see if it follows!
        model_view_etr: View = View.from_str(model_answer)
        model_view_smt_fnode = view_to_smt(model_view_etr)
        premises_etr = question["scoring_guide"]["generation_details"]["premises_etr"]
        premises_view = [View.from_str(p) for p in premises_etr]
        premises_fnodes = [view_to_smt(v) for v in premises_view]

        # Classical logic
        is_classically_correct: bool = does_it_follow(premises_fnodes, model_view_smt_fnode)

        # ETR
        is_etr_predicted: bool = default_procedure_does_it_follow(premises_view, model_view_etr)

        # Exact ETR
        etr_strong_predicted: View = default_inference_procedure(premises_view)
        is_etr_strong_predicted: bool = etr_strong_predicted == model_view_etr

        print(f"ETR predicted: {is_etr_predicted}")
        print(f"Classically correct: {is_classically_correct}")

        return {
            "correct": float(is_classically_correct),
            "is_etr_predicted": float(is_etr_predicted),
            "is_etr_predicted_exact": float(is_etr_strong_predicted),
            "len_response": len(original_model_answer),
            "parse_error": 0,
            "model_answer": model_answer,
            "full_model_response": original_model_answer,

            # Full quadrants
            "correct_and_etr": float(is_classically_correct and is_etr_predicted),
            "correct_and_not_etr": float(is_classically_correct and not is_etr_predicted),
            "not_correct_and_etr": float(not is_classically_correct and is_etr_predicted),
            "not_correct_and_not_etr": float(not is_classically_correct and not is_etr_predicted),
        }
    except Exception as e:
        # print("!" * 80)
        print(f"Error: {str(e)[:100]}")
        # print(json.dumps(question, indent=4))
        # print(model_answer)
        # raise e
        return {
            "correct": 0.0,
            "len_response": len(original_model_answer),
            "parse_error": 1,
            "is_etr_predicted": 0.0,
            "is_etr_predicted_exact": 0.0,
            "model_answer": model_answer,
            "full_model_response": original_model_answer,

            # Full quadrants
            "correct_and_etr": 0.0,
            "correct_and_not_etr": 0.0,
            "not_correct_and_etr": 0.0,
            "not_correct_and_not_etr": 0.0,
        }


def get_etr_substr(answer_text):
    # Show the full details of the question, for debugging. This contains generation details and the scoring guide.
    # print(json.dumps(question, indent=4))
    # If it contains no '{', wrap it in curly brackets
    if "{" not in answer_text:
        answer_text = "{" + answer_text + "}"

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
        raise Exception("Could not find a match in the answer text")
    else:
        # print(f"Matched this answer: {model_answer}")
        pass

    # Let's try to clean up the answer
    # Remove "`." from the end of the answer (but not anywhere else in the string)
    model_answer = model_answer.strip()
    model_answer = re.sub(r"^:", "", model_answer)
    model_answer = re.sub(r"`\.$", "", model_answer)
    model_answer = re.sub(r"`$", "", model_answer)
    model_answer = re.sub(r"\.$", "", model_answer)
    model_answer = re.sub(r"^`", "", model_answer)

    # If there are more than one '{' in the model_answer, and the first character is a '{', remove it and also the last '}'
    if model_answer.count("{") > 1 and model_answer[0] == "{" and model_answer[-1] == "}":
        model_answer = model_answer[1:-1]

    # If there is no '{' in the model, add it to the front, do the same at the back
    if "{" not in model_answer:
        model_answer = "{" + model_answer
    if "}" not in model_answer:
        model_answer = model_answer + "}"

    print(f"Matched and parsed: {model_answer}")
    return model_answer

def use_model_get_etr_text(model_answer: str, short_name_to_full_name: dict[str, str], temperature: float = 0):
    # Reverse short_name_to_full_name
    full_name_to_short_name = {v: k for k, v in short_name_to_full_name.items() if k and v}

    try:
        full_names = [fn for fn in short_name_to_full_name.values() if fn]
        name_options = ', '.join(full_names)
    except Exception as e:
        print(short_name_to_full_name)
        raise e

    prompt = textwrap.dedent(f"""
        I am evaluating a logical claim, and I need to rewrite it into a format I can use.
        
        # The Claim
        {model_answer}
        
        # Needed Format
        I want you to rewrite this answer in the format of a logical statement. Here are the rules for how you should format it:
        - You can write a predicate like "f()"
        - If the predicate has arguments, you can write them like "f(x)"
        - You can do negation with "~", like "~f(x)" to mean "not f(x)"
        - You can represent "and" by writing multiple predicates without a separator, like "f(x)g(x)"
        - You can represent "or" by writing multiple predicates with a "," between them, like "f(x),g(x)"
        - You can use the "∀" to represent "for all", like "∀x f(x)"
        - You can use the "∃" to represent "there exists", like "∃x f(x)"
        - If nothing is concluded, write "{{0}}"
        - Wrap a statement in curly braces, like "{{f(x)g(x)}}", or "∀x {{f(x)g(x)}}", if there's a quantifier
        - Don't use unnecessary parentheses, like write "f(x)g(x)" instead of "(f(x))(g(x))"
        
        You can use these predicates in your answer: {name_options}
        
        Please rewrite the claim in this format. 
        
        Give your answer like this: `Answer: {{f(x)g(x)}}`
    """)
    response = openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=200
    )
    rewritten_by_model = response.choices[0].message.content
    print(f"Rewritten by model: {rewritten_by_model}")
    etr_text = get_etr_substr(rewritten_by_model)

    # Use full_name_to_short_name to convert the etr_text back to the short names
    print(f"Converting {etr_text} back to short names")
    etr_text = etr_text.replace("_", "")
    for full_name, short_name in full_name_to_short_name.items():
        full_name = full_name.replace("_", "")
        etr_text = etr_text.replace(full_name, short_name)
    # print(f"Converted to short names: {etr_text}")

    # Add '()' as needed, so like {B(a)} becomes {B(a())}, so any short name that isn't followed by a '(' should have '()' inserted right after. But only do this if the '(' is not already there.
    for short_name in full_name_to_short_name.values():
        # Look for the short_name not followed by a '('
        pattern = f"({short_name})([^(]|$)"
        etr_text = re.sub(pattern, r"\1()\2", etr_text)
    
    # print(f"Added missing parentheses: {etr_text}")

    # Remove spaces, except the needed spaces
    etr_text = etr_text.replace(" ", "")
    etr_text = etr_text.replace("{", " {").strip()

    print(f"Final ETR text: {etr_text}")

    return etr_text
