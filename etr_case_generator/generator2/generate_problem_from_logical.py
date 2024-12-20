from typing import get_args

from etr_case_generator.generator2.etr_generator import random_etr_problem
from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType, PartialProblem
from etr_case_generator.generator2.full_problem_creator import full_problem_from_smt_problem
from etr_case_generator.ontology import ELEMENTS, Ontology
from etr_case_generator.generator2.smt_generator import random_smt_problem, SMTProblem


def generate_problem(args, ontology: Ontology = ELEMENTS) -> FullProblem:
    # Generate partial problems
    if args.generate_function == "random_smt_problem":
        # TODO(Andrew) Return PartialProblem
        partial_problem: SMTProblem = random_smt_problem(ontology=ontology, total_num_pieces=args.num_pieces)
    elif args.generate_function == "random_etr_problem":
        partial_problem: PartialProblem = random_etr_problem(ontology=ontology)

    # TODO(Andrew) Get PartialProblem instead of SMTProblem

    # TODO(Andrew) Fill out all views in PartialProblems, so they have both logical_form_smt and logical_form_etr
    # TODO use `view_to_smt`

    # Flesh out the problems with text and everything
    full_problem: FullProblem = full_problem_from_smt_problem(partial_problem, ontology=ontology)

    return full_problem
