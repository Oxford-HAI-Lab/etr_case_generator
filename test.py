import random

from pyetr import View, State, SetOfStates

from etr_case_generator.generator import ETRCaseGenerator
from etr_case_generator.ontology import ELEMENTS
from etr_case_generator.reasoning_problem import ReasoningProblem
from etr_case_generator.mutate_view import mutate_view

r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
r.update_premises(premises=[View.get_falsum()])


def mutate_reasoning_problem(
    r: ReasoningProblem, max_premises: int = 3
) -> ReasoningProblem:
    if len(r.premises) > 0 and random.random() < 0.5:
        # Mutate one of the existing premises
        i = random.randint(0, len(r.premises) - 1)
        premises = [p[0] for p in r.premises]
        premises[i] = mutate_view(premises[i])
        r.update_premises(premises=premises)
        return r
    elif len(r.premises) <= max_premises and random.random() < 0.5:
        # Add a new premise
        r.update_premises(premises=[p[0] for p in r.premises] + [View.get_falsum()])
        return r
    else:
        # Mutate query
        r.update_query(query=mutate_view(r.query[0]))
        return r


def ignore_problem(r: ReasoningProblem) -> bool:
    if len(r.premises) == 0:
        return True
    if all([p[0].is_falsum for p in r.premises]):
        return True

    # Hack to ensure that natural language formulations stay short
    if any([len(p[1]) > 100 for p in r.premises]):
        return True
    if len(r.query[1]) > 100:
        return True

    return len(r.premises) <= 1 and r.premises[0][0].is_falsum


def problem_well_formed(r: ReasoningProblem) -> bool:
    if len(r.premises) == 0:
        return False
    if any(
        [p[0].is_falsum or p[0].is_verum or len(p[0].stage) == 0 for p in r.premises]
    ):
        return False
    if any([View.get_verum() in p[0].stage for p in r.premises]):
        return False
    if any([View.get_verum() in p[0].supposition for p in r.premises]):
        return False
    if r.query[0].is_falsum or r.query[0].is_verum:
        return False

    return True


problem_queue = [ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))]

import time

while len(problem_queue) < 100:
    r = problem_queue.pop(0)
    if not ignore_problem(r):
        problem_queue.append(r)
    problem_queue.append(mutate_reasoning_problem(r))

    if problem_well_formed(r):
        print(r.premises)
        print(r.query)
        print(r.full_prose())
    # time.sleep(1)
