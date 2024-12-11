import argparse
import json
import itertools
import random
import textwrap

from pysmt.fnode import FNode

from etr_case_generator import ETRCaseGenerator
from etr_case_generator.ontology import ELEMENTS
from typing import Optional
from dataclasses_json import dataclass_json
from dataclasses import dataclass

from smt_interface.smt_encoder import check_validity


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="etr_for_lm_eval",
        help="Name of the dataset (.jsonl)",
    )
    parser.add_argument(
        "-n",
        "--n-problems",
        type=int,
        default=10,
        help="Number of problems to generate",
    )
    parser.add_argument(
        "--n-constants",
        type=int,
        default=5,
        help="Maximum number of distinct constant values to consider per problem",
    )
    parser.add_argument(
        "--n-predicates",
        type=int,
        default=5,
        help="Maximum number of distinct predicates to consider per problem",
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
        "--print_only",
        action="store_true",
        default=False,
        help="Print problems to stdout instead of saving to file",
    )
    parser.add_argument(
        "--open_ended_questions",
        action="store_true",
        default=False,
        help="Generate questions like \"What if anything follows?\" instead of \"Does X follow?\"",
    )
    args = parser.parse_args()
    return args


def generate_problems_with_set_conclusions(
        generator: ETRCaseGenerator,
        n_problems,
        conclusions_follow_by_etr: Optional[bool],
        conclusions_valid: Optional[bool],
        verbose: bool = False,
        open_ended_questions: bool = False,
):
    problems = []
    if verbose:
        print(
            f"Generating {n_problems} problems. "
            f"ETR={conclusions_follow_by_etr}; Classical={conclusions_valid}"
        )
    while len(problems) < n_problems:
        for p in generator.generate_reasoning_problems(
            n_views=20,
            categorical_conclusions=conclusions_follow_by_etr,
            n_trials_timeout=1000,
            verbose=verbose,
        ):
            if len(problems) >= n_problems:
                break

            # Check if the conclusion is classically valid
            valid_conclusion = check_validity(
                p.premise_views, [p.question_conclusion_view]
            )

            # If we're enforcing a classical conclusion that mismatches, skip this
            # problem
            if conclusions_valid == True and not valid_conclusion:
                if conclusions_follow_by_etr in (False, None):
                    # We can cheat here and force the conclusion to be valid by just
                    # making it one of the premises...
                    premise_to_use = random.choice(range(len(p.premises)))
                    p.question_conclusion_view = p.premise_views[premise_to_use]
                    p.question_conclusion = (
                        p.question_conclusion_view.to_str(),
                        p.premises[premise_to_use][1],
                    )

                    # Sanity check
                    assert check_validity(p.premise_views, [p.question_conclusion_view])
                    valid_conclusion = True

                    p.question_conclusion_is_etr_conclusion = (
                        p.question_conclusion_view == p.etr_conclusion_view
                    )

                    # Reset full question text to match the new conclusion
                    p.full_prose_question = f"Does it follow that {p.question_conclusion[1]}?\n\n"
                    p.full_prose_question += "Answer using 'YES' or 'NO' ONLY."
                else:
                    continue
            if conclusions_valid == False and valid_conclusion:
                continue

            if open_ended_questions:
                # Reset full question to be open-ended
                p.full_prose_question = ""
                p.full_prose_question += "I've rewritten the premises in logical format for you:\n\n"
                for i, (view, premise) in enumerate(p.premises):
                    p.full_prose_question += f" {i+1}. {view}\n"  # TODO Get them in logical form here
                p.full_prose_question += "\n\n"
                p.full_prose_question += textwrap.dedent("""
                    For the purpose of this question, I want you to write your answer in the format of a logical statement. Here are the rules for how you should format it:
                    - You can write a predicate like "f()"
                    - If the predicate has arguments, you can write them like "f(x)"
                    - You can do negation with "~", like "~f(x)" to mean "not f(x)"
                    - You can represent "and" by writing multiple predicates without a separator, like "f(x)g(x)"
                    - You can represent "or" by writing multiple predicates with a "," between them, like "f(x),g(x)"
                    - You can use the "∀" to represent "for all", like "∀x f(x)"
                    - You can use the "∃" to represent "there exists", like "∃x f(x)"
                    - Wrap a statement in curly braces, like "{f(x)g(x)}", or "∀x {f(x)g(x)}", if there's a quantifier
                    """).strip() # TODO Add more rules here
                p.full_prose_question += "\n\nWrite your answer in the logical statement format that I've shown you above.\n\nWhat, if anything, follows from the premises I've given you?\n\nSpend one paragraph thinking, and then write your answer like this: 'The following follows: `{f(x)g(x)}`'."

            # If we want conclusions to follow by ETR, ETR has to predict something
            # categorical and it also has to match the question being asked
            if conclusions_follow_by_etr == True and not (
                p.etr_conclusion_is_categorical
                and p.question_conclusion_is_etr_conclusion
            ):
                continue

            p.classically_valid_conclusion = valid_conclusion

            if verbose:
                print(
                    f"Conclusions: ETR={p.etr_conclusion_is_categorical and p.question_conclusion_is_etr_conclusion}, classical={p.classically_valid_conclusion}"
                )

            if any([len(state) == 0 for state in p.etr_conclusion_view.stage]):
                if verbose:
                    print("Skipping problem with empty state in ETR conclusion")
                continue
            else:
                problems.append(p.to_dict())

    return problems


def main(
    dataset_name: str,
    n_problems: int,
    n_constants: int,
    n_predicates: int,
    balance: bool,
    verbose: bool = False,
    print_only: bool = False,
    open_ended_questions: bool = False,
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
    g = ETRCaseGenerator(ontology=ELEMENTS)
    g.num_constants = n_constants
    g.num_predicates = n_predicates
    dataset = []

    if balance:
        for etr, classical in itertools.product([True, False], repeat=2):
            dataset += generate_problems_with_set_conclusions(
                generator=g,
                n_problems=-(-n_problems // 4),  # Round up
                conclusions_follow_by_etr=etr,
                conclusions_valid=classical,
                verbose=verbose,
                open_ended_questions=open_ended_questions,
            )
    else:
        dataset += generate_problems_with_set_conclusions(
            generator=g,
            n_problems=n_problems,
            conclusions_follow_by_etr=None,
            conclusions_valid=None,
            verbose=verbose,
            open_ended_questions=open_ended_questions,
        )

    formatted_problems = []
    for problem in dataset:
        formatted_problem = {
            "question": problem["full_prose_premises"].strip() + "\n\n" + problem["full_prose_question"].strip(),
            "scoring_guide": {
                **problem,
                "etr_answer": (
                    # ETR says "yes" if it predicts a categorical conclusion and that
                    # conclusion is explicitly what we ask about in the question.
                    "YES"
                    if (
                        problem["etr_conclusion_is_categorical"]
                        and problem["question_conclusion_is_etr_conclusion"]
                    )
                    else "NO"
                ),
                "logically_correct_answer": (
                    "YES" if problem["classically_valid_conclusion"] else "NO"
                ),
            },
        }
        # print(json.dumps(formatted_problem, indent=2))
        formatted_problems.append(formatted_problem)

    if print_only:
        for problem in formatted_problems:
            print(json.dumps(problem, indent=2))

    if not print_only:
        if verbose:
            print(
                f"Saving dataset of length {len(dataset)} to datasets/{dataset_name}.jsonl"
            )
        with open(f"datasets/{dataset_name}.jsonl", "w") as f:
            for problem in formatted_problems:
                f.write(json.dumps(problem) + "\n")


if __name__ == "__main__":
    args = parse_args()
    main(
        dataset_name=args.dataset_name,
        n_problems=args.n_problems,
        n_constants=args.n_constants,
        n_predicates=args.n_predicates,
        balance=args.balance,
        verbose=args.verbose,
        print_only=args.print_only,
        open_ended_questions=args.open_ended_questions,
    )
