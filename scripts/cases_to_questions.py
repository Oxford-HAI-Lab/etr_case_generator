import json
import inspect
import random
from pyetr import cases

from etr_case_generator.reified_problem import FullProblem, QuestionType, PartialProblem

from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name


def get_case_info(case_class):
    info = {
        "name": case_class.__name__,
        "docstring": inspect.getdoc(case_class),
    }
    if hasattr(case_class, 'v'):
        info['v'] = [str(view) for view in case_class.v]
    if hasattr(case_class, 'c'):
        info['c'] = str(case_class.c) if isinstance(case_class.c, cases.View) else ' '.join(str(view) for view in case_class.c)

    # Add prob variable if it exists
    if hasattr(case_class, 'prob'):
        info['prob'] = str(case_class.prob)

    # Add g1 and g2 variables if they exist
    if hasattr(case_class, 'g1'):
        info['g1'] = str(case_class.g1)
    if hasattr(case_class, 'g2'):
        info['g2'] = str(case_class.g2)

    # Add custom functions if they exist
    custom_functions = [attr for attr in dir(case_class) if callable(getattr(case_class, attr)) and not attr.startswith("__")]
    if custom_functions:
        info['custom_functions'] = custom_functions

    return info


def create_question(case, all_cases):
    question = " ".join([str(v) for v in case['v']])
    correct_answer = case['c']

    # Get 3 random wrong answers
    wrong_answers = []
    while len(wrong_answers) < 3:
        random_case = random.choice(all_cases)
        if random_case != case and random_case['c'] not in wrong_answers:
            wrong_answers.append(random_case['c'])

    choices = wrong_answers + [correct_answer]
    random.shuffle(choices)

    # Ensure all choices are strings
    choices = [str(choice) for choice in choices]

    return {
        "question": question,
        "choices": choices,
        "answer": choices.index(str(correct_answer))
    }


def main():
    all_cases = []
    for name, obj in inspect.getmembers(cases):
        if inspect.isclass(obj) and issubclass(obj, cases.BaseExample) and obj != cases.BaseExample:
            all_cases.append(get_case_info(obj))

    questions = [create_question(case, all_cases) for case in all_cases]

    # TODO: These need to be FullProblems
    # TODO: Use a random ontology for each FullProblem
    # TODO: Generate n FullProblems for each question

    with open('lm_eval/tasks/formal_questions/questions.jsonl', 'w') as f:
        for question in questions:
            f.write(json.dumps(question) + '\n')


if __name__ == "__main__":
    main()
