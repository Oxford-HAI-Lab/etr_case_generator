import copy
import json
import random

from pyetr import View, State, SetOfStates

from etr_case_generator.generator import ETRCaseGenerator
from etr_case_generator.ontology import ELEMENTS
from etr_case_generator.reasoning_problem import ReasoningProblem
from etr_case_generator.mutate_view import mutate_view
import multiprocessing

r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
r.update_premises(
    premises=[
        View.from_str("Ex { S(x*) D(x) }"),
        View.from_str("{ S(T()*) }"),
    ]
)
r.update_query(query=View.from_str("{D(T())}"))


def mutate_reasoning_problem(
    r: ReasoningProblem, max_premises: int = 5
) -> list[ReasoningProblem]:
    def add_premise(r: ReasoningProblem) -> ReasoningProblem:
        r = copy.deepcopy(r)
        if len(r.premises) < max_premises:
            r.update_premises(premises=[p[0] for p in r.premises] + [View.get_falsum()])
        return r

    def remove_premise(r: ReasoningProblem) -> ReasoningProblem:
        r = copy.deepcopy(r)
        if len(r.premises) > 0:
            r.update_premises(premises=[p[0] for p in r.premises[:-1]])
        return r

    def mutate_premise(r: ReasoningProblem) -> ReasoningProblem:
        r = copy.deepcopy(r)
        if len(r.premises) > 0:
            i = random.randint(0, len(r.premises) - 1)
            premises = [p[0] for p in r.premises]
            premises[i] = mutate_view(premises[i])
            r.update_premises(premises=premises)
        return r

    def mutate_query(r: ReasoningProblem) -> ReasoningProblem:
        r = copy.deepcopy(r)
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


def worker(proc_num, queue):
    local_problem_queue = copy.deepcopy(queue)
    local_ret = []
    try:
        while len(local_problem_queue) > 0 and len(local_ret) < 100:
            r = local_problem_queue.pop(0)
            mutations = mutate_reasoning_problem(r)
            for m in mutations:
                if problem_well_formed(m):
                    local_problem_queue.append(m)
                    if m.query_is_logically_consistent or m.etr_predicts_query_follows:
                        local_ret.append(m)

            print(
                f"Process {proc_num}: "
                + str(len(local_problem_queue))
                + "\t"
                + str(len(local_ret))
                + "\t"
                + str(
                    sum(
                        [1 if r.etr_conclusion_is_categorical else 0 for r in local_ret]
                    )
                )
                + "\t"
                + str(
                    sum([1 if r.etr_predicts_query_follows else 0 for r in local_ret])
                )
            )
    except KeyboardInterrupt:
        with open(f"output_{proc_num}.jsonl", "w") as f:
            for r in local_ret:
                f.write(json.dumps(r.to_dict()) + "\n")
        exit(0)

    with open(f"output_{proc_num}.jsonl", "w") as f:
        for r in local_ret:
            f.write(json.dumps(r.to_dict()) + "\n")

    print(f"Process {proc_num} finished")


if __name__ == "__main__":

    # r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
    # r.update_premises(
    #     premises=[
    #         View.from_str("{PP(TA())PQ(TA()), PR(TA())PS(TA())}"),
    #         View.from_str("{PP(TA())}"),
    #     ]
    # )
    # r.update_query(query=View.from_str("{PQ(TA())}"))

    queue = []

    # r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
    # r.update_premises(
    #     premises=[
    #         View.from_str("{PQ(TA())}^{PP(TA())}"),
    #         View.from_str("{PP(TA())}"),
    #     ]
    # )
    # r.update_query(query=View.from_str("{PQ(TA())}"))

    # queue.append(r)

    r = ReasoningProblem(generator=ETRCaseGenerator(ELEMENTS))
    r.update_premises(
        premises=[
            View.from_str("Ax Ay {PQ(y)}^{PP(x)}"),
            View.from_str("{Ax Ay {PR(y)}^{PQ(x)}}"),
        ]
    )
    r.update_query(query=View.from_str("Ax Ay {PP(TA())}"))

    queue.append(r)

    processes = []
    for i in range(16):
        p = multiprocessing.Process(target=worker, args=(i, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Write the output to a single file
    with open("multi_processed_output.jsonl", "w") as f:
        for i in range(8):
            with open(f"output_{i}.jsonl", "r") as f2:
                f.write(f2.read())


# ret = []
# try:
#     while len(problem_queue) > 0 and len(ret) < 10:
#         r = problem_queue.pop(0)
#         mutations = mutate_reasoning_problem(r)
#         # if not ignore_problem(r):
#         #     problem_queue.append(r)
#         for m in mutations:
#             if problem_well_formed(m):
#                 problem_queue.append(m)
#                 if m.query_is_logically_consistent or m.etr_predicts_query_follows:
#                     ret.append(m)

#         print(
#             str(len(problem_queue))
#             + "\t"
#             + str(len(ret))
#             + "\t"
#             + str(sum([1 if r.etr_conclusion_is_categorical else 0 for r in ret]))
#             + "\t"
#             + str(sum([1 if r.etr_predicts_query_follows else 0 for r in ret]))
#         )
#         #     print(f"Vocab size: {r.vocab_size}")
#         #     # print(r.premises)
#         #     # print(r.query)
#         #     print(r.full_prose())
#         # time.sleep(1)
# except KeyboardInterrupt:
#     with open("output_2.jsonl", "w") as f:
#         for r in ret:
#             f.write(json.dumps(r.to_dict()) + "\n")
#     exit(0)

# with open("output_2.jsonl", "w") as f:
#     for r in ret:
#         f.write(json.dumps(r.to_dict()) + "\n")
#     # json.dump([r.to_dict() for r in ret], f, indent=4)
