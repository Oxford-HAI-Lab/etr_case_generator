import argparse
import json
from tqdm import tqdm

from pysmt.fnode import FNode

from etr_case_generator import ETRCaseGenerator
from etr_case_generator.ontology import CARDS
from typing import Optional
from dataclasses_json import dataclass_json
from dataclasses import dataclass


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument("--dataset_name", type=str, default="etr_for_lm_eval.jsonl", help="Name of the dataset (.jsonl)")
    parser.add_argument(
        "-n",
        "--n_problems",
        type=int,
        default=10,
        help="Number of problems to generate",
    )
    parser.add_argument(
        "--categorical_conclusions",
        choices=["all", "parity", "random"],
        default="all",
        help="Enforce ETR conclusions are categorical in all problems, or enforce parity, or nothing",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    parser.add_argument(
        "--print_only",
        action="store_true",
        default=False,
        help="Print problems to stdout instead of saving to file",
    )
    parser.add_argument(
        "--balance_set",
        action="store_true",
        default=False,
        help="If true, it requires that the resulting dataset has an equal number of problems where the ETR answer is YES or NO, and within each of those bins, an equal number where the classical answer is YES or NO, in 1/4 splits.",
    )
    args = parser.parse_args()
    return args


def generate_reasoning_problems(
    generator: ETRCaseGenerator,
    n_problems,
    require_categorical: Optional[bool],
    verbose: bool = False,
    balance: bool = False,

):
    problems = []
    pbar = tqdm(total=n_problems, desc="Generating problems")

    bins = {}
    if balance:
        for etr_answer in [True, False]:
            for classical_answer in [True, False]:
                bins[(etr_answer, classical_answer)] = 0

    max_overgeneralize = n_problems * 4
    i = 0

    while len(problems) < n_problems:  # TODO Is this necessary?
        if i > max_overgeneralize:
            break
        for p in generator.generate_reasoning_problems(
            n_views=20,
            categorical_conclusions=require_categorical,
            n_trials_timeout=1000,
            verbose=verbose,
        ):
            i += 1
            if i > max_overgeneralize:
                break
            if len(problems) >= n_problems:
                break

            if balance:
                key = (p.question_conclusion_is_etr_conclusion, p.classically_valid_conclusion)
                if bins[key] >= n_problems / 4:
                    continue
                bins[key] += 1

            problems.append(p.to_dict())
            pbar.update(1)
        # if verbose:
        #     print("===> Retrying... Dataset so far: ", len(problems))

    return problems


def main(
    dataset_name: str, n_problems: int, categorical_conclusions: str, verbose: bool,
    print_only: bool = False
):
    # For now, we're just working with cards (and cards only work with basic objects)
    g = ETRCaseGenerator(ontology=CARDS)
    dataset = []

    if categorical_conclusions == "parity":
        for require_categorical in [True, False]:
            dataset += generate_reasoning_problems(
                generator=g,
                n_problems=n_problems / 2,
                require_categorical=require_categorical,
                verbose=verbose,
            )
    else:
        require_categorical = None
        if categorical_conclusions == "all":
            require_categorical = True

        dataset += generate_reasoning_problems(
            generator=g,
            n_problems=n_problems,
            require_categorical=require_categorical,
            verbose=verbose,
        )


    formatted_problems = []
    for problem in dataset:
        formatted_problem = {
            "question": problem["full_prose"],
            "scoring_guide": {
                **problem,
                "etr_answer": "YES" if problem["question_conclusion_is_etr_conclusion"] else "NO",
                "logically_correct_answer": "YES" if problem["classically_valid_conclusion"] else "NO",
            }
        }
        print(json.dumps(formatted_problem, indent=2))
        formatted_problems.append(formatted_problem)
        
    if not print_only:
        if verbose:
            print(
                f"Saving dataset of length {len(dataset)} to datasets/{dataset_name}"
            )
        with open(f"datasets/{dataset_name}", "w") as f:
            for problem in formatted_problems:
                f.write(json.dumps(problem) + "\n")


if __name__ == "__main__":
    args = parse_args()
    main(
        dataset_name=args.dataset_name,
        n_problems=args.n_problems,
        categorical_conclusions=args.categorical_conclusions,
        verbose=args.verbose,
        print_only=args.print_only
    )
