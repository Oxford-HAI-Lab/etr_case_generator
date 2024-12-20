from typing import get_args

from etr_case_generator.generator2.etr_generator import random_etr_problem
from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType, PartialProblem
from etr_case_generator.generator2.full_problem_creator import full_problem_from_partial_problem
from etr_case_generator.ontology import ELEMENTS, Ontology
from etr_case_generator.generator2.smt_generator import random_smt_problem, SMTProblem


def generate_problem(args, ontology: Ontology = ELEMENTS) -> FullProblem:
    # Generate partial problems
    if args.generate_function == "random_smt_problem":
        smt_problem: SMTProblem = random_smt_problem(ontology=ontology, total_num_pieces=args.num_pieces)
        partial_problem = smt_problem.to_partial_problem()
    elif args.generate_function == "random_etr_problem":
        partial_problem: PartialProblem = random_etr_problem(ontology=ontology)
    else:
        raise ValueError(f"Unknown generate_function: {args.generate_function}")

    # Fill out the partial problem as much as possible, e.g. fill in the ETR from the SMT and vice versa
    partial_problem.fill_out(ontology=ontology)
    partial_problem.add_etr_predictions(ontology=ontology)
    partial_problem.add_classical_logic_predictions()

    # Flesh out the problems with text and everything
    full_problem: FullProblem = full_problem_from_partial_problem(partial_problem, ontology=ontology)

    return full_problem
