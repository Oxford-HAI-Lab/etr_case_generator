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
) -> list[ReasoningProblem]:
    def add_premise(r: ReasoningProblem) -> ReasoningProblem:
        if len(r.premises) < max_premises:
            r.update_premises(premises=[p[0] for p in r.premises] + [View.get_falsum()])
        return r

    def remove_premise(r: ReasoningProblem) -> ReasoningProblem:
        if len(r.premises) > 0:
            r.update_premises(premises=[p[0] for p in r.premises[:-1]])
        return r

    def mutate_premise(r: ReasoningProblem) -> ReasoningProblem:
        if len(r.premises) > 0:
            i = random.randint(0, len(r.premises) - 1)
            premises = [p[0] for p in r.premises]
            premises[i] = mutate_view(premises[i])
            r.update_premises(premises=premises)
        return r

    def mutate_query(r: ReasoningProblem) -> ReasoningProblem:
        r.update_query(query=mutate_view(r.query[0]))
        return r

    mutations = [add_premise, remove_premise, mutate_premise, mutate_query]
    return [m(r) for m in mutations]


def ignore_problem(r: ReasoningProblem) -> bool:
    if len(r.premises) == 0:
        return True
    if all([p[0].is_falsum for p in r.premises]):
        return True

    # Ensure that natural language formulations stay short
    if r.vocab_size > 10:
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
    if len(r.query[0].stage) == 0:
        return False
    if r.vocab_size > 10:
        return False

    return True


r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
r.update_premises(
    premises=[View.from_str("{P(A())Q(A()), R(A())S(A())}"), View.from_str("{P(A())}")]
)
r.update_query(query=View.from_str("{Q(A())}"))

problem_queue = [r]

import time

ret = []
while len(problem_queue) > 0 and len(ret) < 100:
    r = problem_queue.pop(0)
    mutations = mutate_reasoning_problem(r)
    # if not ignore_problem(r):
    #     problem_queue.append(r)
    for m in mutations:
        if problem_well_formed(m):
            ret.append(m)
            problem_queue.append(m)

    print(len(problem_queue))
    #     print(f"Vocab size: {r.vocab_size}")
    #     # print(r.premises)
    #     # print(r.query)
    #     print(r.full_prose())
    # time.sleep(1)
import json

with open("output.json", "w") as f:
    json.dump([r.to_dict() for r in ret], f, indent=4)
