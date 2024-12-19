from typing import get_args

from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType
from etr_case_generator.generator2.full_problem_creator import full_problem_from_smt_problem
from etr_case_generator.ontology import ELEMENTS, Ontology
from etr_case_generator.generator2.smt_generator import random_smt_problem, SMTProblem


def generate_problem_in_smt(args, ontology: Ontology=ELEMENTS) -> FullProblem:
    smt_problem: SMTProblem = random_smt_problem(ontology=ontology, total_num_pieces=args.num_pieces)
    full_problem: FullProblem = full_problem_from_smt_problem(smt_problem, ontology=ontology)
    return full_problem
