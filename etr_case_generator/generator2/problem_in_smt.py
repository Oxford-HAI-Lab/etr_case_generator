from etr_case_generator.generator2.reified_problem import FullProblem, full_problem_from_smt_problem
from etr_case_generator.ontology import ELEMENTS, Ontology
from etr_case_generator.smt_generator import random_smt_problem


def generate_problem_in_smt(args, ontology: Ontology=ELEMENTS) -> FullProblem:
    smt_problem = random_smt_problem(args)
    full_problem = full_problem_from_smt_problem(smt_problem)
    return full_problem
