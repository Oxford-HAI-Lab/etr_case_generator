import argparse
import json

from pysmt.fnode import FNode

from etr_case_generator import ETRCaseGenerator
from etr_case_generator.ontology import CARDS
from typing import Optional
from dataclasses_json import dataclass_json
from dataclasses import dataclass

from smt_interface.smt_encoder import check_validity


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
        "--balance",
        action="store_true",
        default=False,
        help="Whether to enforce balanced conclusions between ETR and classical validity.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        default=False,
        help="Print problems to stdout instead of saving to file",
    )
    args = parser.parse_args()
    return args


def generate_reasoning_problems(
    generator: ETRCaseGenerator,
    n_problems,
    require_etr_categorical: Optional[bool],
    require_valid: bool,
    verbose: bool = False,
):
    problems = []
    while len(problems) < n_problems:
        for p in generator.generate_reasoning_problems(
            n_views=20,
            categorical_conclusions=require_etr_categorical,
            n_trials_timeout=1000,
            verbose=verbose,
        ):
            if len(problems) >= n_problems:
                break

            # Check if the conclusion is classically valid
            p.classically_valid_conclusion = check_validity(p.premise_views, [p.question_conclusion_view])
            if verbose:
                print(f"Classical validity: {p.classically_valid_conclusion}")

            problems.append(p.to_dict())
        # if verbose:
        #     print("===> Retrying... Dataset so far: ", len(problems))

    return problems


def main(
    dataset_name: str,
    n_problems: int,
    balance: bool,
    verbose: bool = False,
    print_only: bool = False
):
    """Generate ETR problems for use in lm_eval.

    Args:
        dataset_name (str): The name of the dataset to write.
        n_problems (int): The size of the dataset to generate.
        balance (bool): Whether the dataset should be balanced between ETR and classical
            validity. If true, enforces the confusion matrix between "follows by ETR"
            and "follows classically" to be balanced.
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
        print_only (bool, optional): Whether to just print results and not save them to
            a file. Defaults to False.
    """
    # For now, we're just working with cards (and cards only work with basic objects)
    g = ETRCaseGenerator(ontology=CARDS)
    dataset = []

    if balance:
        for require_categorical in [True, False]:
            dataset += generate_reasoning_problems(
                generator=g,
                n_problems=n_problems / 2,
                require_etr_categorical=require_categorical,
                require_valid=True,
                verbose=verbose,
            )
    else:
        require_categorical = None
        if categorical_conclusions == "all":
            require_categorical = True

        dataset += generate_reasoning_problems(
            generator=g,
            n_problems=n_problems,
            require_etr_categorical=require_categorical,
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
        balance=args.balance,
        verbose=args.verbose,
        print_only=args.print_only
    )
