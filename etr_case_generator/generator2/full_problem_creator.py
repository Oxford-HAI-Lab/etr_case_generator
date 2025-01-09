import random

from etr_case_generator import Ontology
from etr_case_generator.generator2.etr_logic import get_etr_conclusion
from etr_case_generator.generator2.formatting_smt import format_smt, smt_to_etr, smt_to_english
from etr_case_generator.generator2.reified_problem import FullProblem, ReifiedView, PartialProblem, Conclusion
from etr_case_generator.ontology import ELEMENTS
from etr_case_generator.generator2.smt_generator import SMTProblem


def full_problem_from_partial_problem(partial_problem: PartialProblem, ontology: Ontology=ELEMENTS) -> FullProblem:
    """Convert an SMTProblem to a FullProblem, including yes/no and multiple choice conclusions."""

    possible_conclusions: list[Conclusion] = []
    if partial_problem.possible_conclusions_from_logical:
        possible_conclusions.extend(partial_problem.possible_conclusions_from_logical)
    if partial_problem.possible_conclusions_from_etr:
        possible_conclusions.extend(partial_problem.possible_conclusions_from_etr)

    # TODO, A smarter method for selecting multiple choice options, getting a good mix of answers, making sure there's exactly one correct answer
    multiple_choices: list[Conclusion] = possible_conclusions.copy()[:4]

    random.shuffle(multiple_choices)
    random.shuffle(possible_conclusions)

    # Determine the ETR predicted conclusion
    if partial_problem.etr_what_follows is not None:
        etr_predicted_conclusion = partial_problem.etr_what_follows
    else:
        etr_predicted_conclusion = get_etr_conclusion(views=partial_problem.premises)

    full_problem = FullProblem(
        introductory_prose=ontology.introduction,
        views=partial_problem.premises,
        # Yes/No section
        possible_conclusions=possible_conclusions if possible_conclusions else None,
        # Multiple choice section
        multiple_choices=multiple_choices if multiple_choices else None,
        # Open ended question
        etr_predicted_conclusion=Conclusion(view=etr_predicted_conclusion),
    )

    full_problem.fill_out(ontology=ontology, partial_problem=partial_problem)

    return full_problem
