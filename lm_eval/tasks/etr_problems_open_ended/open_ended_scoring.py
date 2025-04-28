import json
import re
import os
import sys
import textwrap
import openai

from pyetr import View
from pysmt.fnode import FNode
from pysmt.shortcuts import is_valid
from etr_case_generator.formatting_smt import load_fnode_from_string
from etr_case_generator.logic_helper import does_it_follow
from pyetr.inference import default_procedure_does_it_follow
from pyetr.inference import default_inference_procedure
from pyetr.issues import IssueStructure
from smt_interface.smt_encoder import view_to_smt

# This is necessary because of the way that lm_eval runs this file
sys.path.append(os.getcwd())

def set_openai_key():
    # Handle API key swapping for OpenRouter
    original_openai_key = os.getenv("ORIGINAL_OPENAI_KEY")
    if original_openai_key:
        os.environ["OPENAI_API_KEY"] = original_openai_key
    else:
        # If no original key stored, use the current OPENAI_API_KEY
        openai.api_key = os.getenv("OPENAI_API_KEY")

    # Execute (source) the file `/home/keenan/Dev/private_keys.sh` if it exists
    if os.path.exists("/home/keenan/Dev/private_keys.sh"):
        os.system("source /home/keenan/Dev/private_keys.sh")
        found_api_key = os.getenv("OPENAI_API_KEY")
        print("Ran file to find API key")
    # else:
    #     print("No file to run to find API key")

    # # Print for debugging
    # print(f"Original OpenAI Key: {original_openai_key}")
    # print(f"Current OpenAI Key: {openai.api_key}")
    # print(f"Found API Key: {found_api_key}")


def score_answer(question, model_answer):
    """
    Score the given answer based on whether it correctly identifies if the conclusion follows.

    Args:
        question (dict): A dictionary containing the question and scoring guide
        model_answer (str or dict): The model's response to the ETR question

    Returns:
        dict: A dictionary containing the score and response length
    """
    set_openai_key()

    # Extract answer text
    if isinstance(model_answer, dict):
        answer_text = model_answer.get("text", "")
    elif isinstance(model_answer, list) and len(model_answer) > 0:
        answer_text = str(model_answer[0])
    else:
        answer_text = str(model_answer)
    original_model_answer: str = answer_text
    print("-" * 80)
    print(f"Starting Open Ended Scoring. Got this answer text: `{answer_text}`")

    num_attempts = 3
    for i in range(num_attempts):
        if len(answer_text.strip()) == 0:
            print("Empty answer text, debug printing, returning early")
            print(model_answer)
            break
        try:
            return attempt_score_answer(question, answer_text, original_model_answer, attempt_num=i)
        except Exception as e:
            print(f"!!!! Failure {i+1}/{num_attempts}: {str(e)[:100]}...")
            if i == num_attempts - 1:
                break
            continue
    return {
        "correct": 0.0,
        "len_response": len(original_model_answer),
        "parse_error": 1,  # This is the important part here. The rest are just filled in to prevent errors
        "is_etr_predicted": 0.0,
        "is_etr_predicted_exact": 0.0,
        "is_logically_equivalent": 0.0,
        "model_answer": answer_text,
        "full_model_response": original_model_answer,

        # Full quadrants
        "correct_and_etr": 0.0,
        "correct_and_not_etr": 0.0,
        "not_correct_and_etr": 0.0,
        "not_correct_and_not_etr": 0.0,
    }


def attempt_score_answer(question: dict, answer_text: str, original_model_answer: str, attempt_num: int = 0):
    try:
        short_name_to_full_name: dict[str, str] = question["scoring_guide"]["open_ended"]["short_name_to_full_name"]
        model_answer = use_model_get_etr_text(answer_text, short_name_to_full_name, question["scoring_guide"]["generation_details"]["premises_etr"], temperature=0.2 + 0.2 * attempt_num)

        print(f"Compare to predicted:", question["scoring_guide"]["etr_predicted"])

        # Try to see if it follows!
        model_view_etr: View = View.from_str(model_answer)  # Assuming that this doesn't inclue any issue structure by default...
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

        # Replace with an empty issue structure
        etr_strong_predicted = View(
            stage=etr_strong_predicted.stage,
            supposition=etr_strong_predicted.supposition,
            dependency_relation=etr_strong_predicted.dependency_relation,
            issue_structure=IssueStructure(),
            weights=etr_strong_predicted.weights
        )
        # 1. should be equivalence under arbitrary object substitution
        # 2. should be compared after stripping all issue structure out
        is_etr_strong_predicted: bool = etr_strong_predicted.is_equivalent_under_arb_sub(model_view_etr)

        # Check logical equivalence between the strong prediction and model's answer
        # Convert both to PySMT fnodes (already done above)
        # We want to test if etr_strong_predicted and model_view_etr are equivalent
        strong_predicted_smt = view_to_smt(etr_strong_predicted)
        model_view_smt = view_to_smt(model_view_etr)
        # Create the equivalence formula: (P ⟺ Q) using the Iff operator
        equivalence_formula = strong_predicted_smt.Iff(model_view_smt)
        # Check if this equivalence is valid (i.e., is a tautology)
        is_logical_equivalent = is_valid(equivalence_formula)
        print(f"Logical equivalence: {is_logical_equivalent}")
        
        # This can be additionally considered in the scoring if needed
        # For now we'll just track it but not change the result

        print(f"ETR predicted: {is_etr_predicted}")
        print(f"Classically correct: {is_classically_correct}")

        # TODO: If you add a key here, also add it to samples_jsonl_to_csv.py!
        return {
            "correct": float(is_classically_correct),
            "is_etr_predicted": float(is_etr_predicted),
            "is_etr_predicted_exact": float(is_etr_strong_predicted),
            "is_logically_equivalent": float(is_logical_equivalent),
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
        raise e


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

def use_model_get_etr_text(model_answer: str, short_name_to_full_name: dict[str, str], premises: list[str], temperature: float = 0):
    # Reverse short_name_to_full_name
    # Here, "short names" are useful for logical statements, and they might be like "matterEating", and "long names" are for English, like "matter eating"
    full_name_to_short_name = {v: k for k, v in short_name_to_full_name.items() if k and v}

    # Generate some example premises
    full_premises: list[str] = []
    for p in premises:
        # TODO Why did this ever seem like a good idea?
        # for full_name, short_name in full_name_to_short_name.items():
        #     p = p.replace(short_name, full_name)
        full_premises.append(p)

    try:
        short_names = [sn for sn in short_name_to_full_name.keys() if sn]
        name_options = ', '.join(short_names)
    except Exception as e:
        print("Contents of short_name_to_full_name:", short_name_to_full_name)
        raise e

    prompt = textwrap.dedent(f"""
        I am evaluating a logical claim, and I need to rewrite it into a format I can use.
        
        # The Claim
        {model_answer}
        
        # Needed Format
        I want you to write your answer in the format of a logical statement. Here are the rules for how you should format it:
        
        Basic Structure:
        - Every logical statement must be wrapped in curly braces, like "{{...}}"
        - Inside the braces, you can express conjunctions (and) and disjunctions (or)
        - Commas separate different disjuncts (the "or" parts). You can also write "∨" between them instead of commas, like "{{Red(cat()) ∨ Furry(cat())}}"
        - When there are no commas between atoms, they are conjoined (joined with "and"). You can also write "∧" between them instead of commas, like "{{Red(cat()) ∧ Furry(cat())}}"
        - Every atom must have parentheses, even with no arguments
        - All names are CamelCase or camelCase, and they never have spaces in them
        Examples:
        - Write "the cat is red" as "{{Red(cat())}}"
        - Write "the cat is red and furry" as "{{Red(cat())Furry(cat())}}"
        - Write "the cat is red or furry" as "{{Red(cat()),Furry(cat())}}"
        - Write "the cat is red and furry, or the dog is tall" as "{{Red(cat())Furry(cat()),Tall(dog())}}"
        - If nothing is concluded, write "0" or "{{0}}"
        
        Atoms and Terms:
        - Atoms are predicates applied to terms: "Red(cat())", "Likes(dog(),cat())"
        - There are two kinds of terms:
        1. Functional terms: must have parentheses like "cat()" or "pet(dog())"
        2. Arbitrary objects: no parentheses, only used with quantifiers, like "x" in "∀x"
        - Negation uses "~", like "~Red(cat())" to mean "not Red(cat())"
        
        Conjunction and Disjunction:
        - Write "the cat is red and furry" as "{{Red(cat())Furry(cat())}}"
        - Write "the cat is red or furry" as "{{Red(cat()),Furry(cat())}}"
        
        Quantifiers:
        - Universal quantifiers "∀" and existential "∃" go before the braces
        - Only arbitrary objects (without parentheses) can be quantified
        - Write "everything likes cats" as "∀x {{Likes(x,cat())}}"
        - If there is no quantifier, do not write any "∀" or "∃", just {{...}}
        - Only include a quantifier like "∃x" if x appears in the statement
        
        Logical Relationships:
        - Write "if the cat is red then it is furry" as "{{~Red(cat()),Furry(cat())}}"
        - Write "being red implies being furry" as "{{~Red(cat()),Furry(cat())}}"
        
        Examples:
        - Write "the cat is red" as "{{Red(cat())}}"
        - Write "the cat is red and furry" as "{{Red(cat())Furry(cat())}}"
        - Write "the cat is red or furry" as "{{Red(cat()),Furry(cat())}}"
        - Write "if the cat is red then it is furry" as "{{~Red(cat()),Furry(cat())}}"
        - Write "everything likes cats" as "∀x {{Likes(x,cat())}}"
        
        # Predicates
        You can ONLY use these predicates in your answer. You may not use any other terms, you MUST use only these: {name_options}
        Here are some examples of logical formulas that are formatted this way, also showing the predicates you may use: PREMISES_STR
        
        Please rewrite the claim in this format. Do not comment or try to fix the claim, just format it correctly.
        
        Give your answer like this: `Answer: {{f(x)g(x)}}`
    """).replace("PREMISES_STR", "\n".join(full_premises))  # Doing it this way to not mess up textwrap
    # print("Name Options:", name_options)
    # print("Premises:", ", ".join(full_premises))
    # print("Name Substitutions:", short_name_to_full_name)
    response = openai.chat.completions.create(
        model="gpt-4.1-mini",  # 20 times cheaper than gpt-4!
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=200
    )
    rewritten_by_model = response.choices[0].message.content
    print(f"Rewritten by model: {rewritten_by_model}")
    etr_text = get_etr_substr(rewritten_by_model)

    # Why did this ever seem like a good idea?
    # Use full_name_to_short_name to convert the etr_text back to the short names
    # print(f"Converting {etr_text} back to short names")
    # etr_text = etr_text.replace("_", "")
    # for full_name, short_name in full_name_to_short_name.items():
    #     full_name = full_name.replace("_", "")
    #     # Use word boundaries \b to prevent partial matches
    #     etr_text = re.sub(fr'\b{re.escape(full_name)}\b', short_name, etr_text)
    # print(f"Converted to short names: {etr_text}")

    # Convert logical symbols
    etr_text = etr_text.replace(" ∧ ", "∧")
    etr_text = etr_text.replace(" ∨ ", "∨")
    etr_text = etr_text.replace("∧", "")  # Conjunction is represented with concatenation
    etr_text = etr_text.replace("∨", ",")  # Disjunction is represented with commas

    # Check that all predicate names in the ETR text match the allowed names (case-insensitive)
    predicates = re.findall(r'[a-zA-Z]+(?=\()', etr_text)
    valid_names = set(full_name_to_short_name.values())
    
    for pred in predicates:
        if pred not in valid_names:
            # Try case-insensitive match
            matches = [valid for valid in valid_names 
                      if valid.lower() == pred.lower()]
            if matches:
                # Replace with correct case version
                etr_text = re.sub(fr'\b{pred}\b', matches[0], etr_text)
            else:
                print(f"Warning: Predicate {pred} not found in valid names {valid_names}")
                raise ValueError(f"Predicate {pred} not found in valid names {valid_names}")

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
