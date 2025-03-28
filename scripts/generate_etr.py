import traceback
import argparse
import json
import math
import random
from typing import get_args
from collections import Counter
from tqdm import tqdm

from etr_case_generator.etr_generator import set_queue_sizes
from etr_case_generator.etr_generator_no_queue import ETRGeneratorIndependent
from etr_case_generator.generate_problem_from_logical import generate_problem
from etr_case_generator.reified_problem import FullProblem, QuestionType, PartialProblem
from etr_case_generator.logic_types import AtomCount

from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name


def generate_problem_list(n_problems: int, args, question_types: list[str]) -> list[FullProblem]:
    """Generate ETR problems with optional balancing constraints.

    Args:
        n_problems (int): The number of problems to generate
        args: Command line arguments including balancing options
        question_types (list[str]): List of question types to generate

    The function can balance problems in two ways:
    - By quadrants (erotetic vs classical correctness) when args.balance_quadrants is True
    - By ETR agreement (50-50 split on ETR conclusion matching classical) when args.balance_etr_agreement is True
    """
    all_ontologies: list[Ontology] = get_all_ontologies()

    for o in all_ontologies:
        o.preferred_name_shortening_scheme = args.name_shortening
        o.fill_mapping()

    # Initialize tracking based on balancing mode
    if args.balance_quadrants:
        balance_counts = {
            (True, True): 0,   # (erotetic, classical)
            (True, False): 0,  # (erotetic, non-classical)
            (False, True): 0,  # (non-erotetic, classical)
            (False, False): 0  # (non-erotetic, non-classical)
        }
        num_needed_per_category = (n_problems + 3) // 4
    elif args.balance_etr_agreement:
        balance_counts = {True: 0, False: 0}  # Tracks agreement between ETR and classical
        num_needed_per_category = n_problems // 2
    else:
        balance_counts = None
        num_needed_per_category = n_problems

    # Initialize atom count tracking
    num_atoms_counts = {i: 0 for i in args.num_atoms_set} if args.num_atoms_set else {}
    counts_by_atom = {}
    if args.num_atoms_set:
        num_needed_per_category_by_atom = num_needed_per_category // len(args.num_atoms_set)
        print(f"Generating {num_needed_per_category_by_atom} problems per category per atom count.")
        for size in args.num_atoms_set:
            if args.balance_quadrants:
                counts_by_atom[size] = {
                    (True, True): 0, (True, False): 0,
                    (False, True): 0, (False, False): 0
                }
            elif args.balance_etr_agreement:
                counts_by_atom[size] = {True: 0, False: 0}
            else:
                counts_by_atom[size] = 0

    pbar_postfix = {}

    # Track errors and their example messages
    exception_type_counter = Counter[str]()
    exception_examples = {}  # Store first example of each error type

    problem_generator = ETRGeneratorIndependent(seed_bank=args.seed_bank)
    count_per_size = math.ceil(n_problems / len(args.num_atoms_set)) if args.num_atoms_set else 0
    print(f"Balancing by: {'Quadrants' if args.balance_quadrants else 'ETR agreement' if args.balance_etr_agreement else 'Not balancing'}.")
    if args.num_atoms_set:
        print(f"Generating {n_problems} problems with {count_per_size} problems per atom count, across {len(args.num_atoms_set)} atom counts.")

    problems: list[FullProblem] = []
    pbar = tqdm(range(n_problems), desc="Generating problems")
    for _ in pbar:
        current_counter: int = 0
        while True:  # Keep trying until we get an acceptable problem
            ontology = random.choice(all_ontologies)
            current_counter += 1
            
            try:
                # Calculate remaining capacity needed for each atom count
                needed_counts = Counter[AtomCount]()
                if args.num_atoms_set:
                    for size in args.num_atoms_set:
                        remaining = count_per_size - num_atoms_counts[size]
                        needed_counts[AtomCount(size)] = remaining

                problem: FullProblem = generate_problem(args, ontology=ontology, needed_counts=needed_counts, generator=problem_generator)

                # This is helpful for small numbers of atom counts, but it gets annoying for large numbers
                # if args.num_atoms_set:
                #     for na, c in num_atoms_counts.items():
                #         pbar_postfix[f"NA{na}"] = c

                # Get problem characteristics
                conclusion = problem.etr_predicted_conclusion
                problem_is_erotetic = conclusion.is_etr_predicted
                assert problem_is_erotetic, "ETR predicted conclusion should be erotetic by definition"
                problem_is_classical = conclusion.is_classically_correct

                if args.etr_only_wrong and problem_is_classical:
                    # print("Skipping problem because ETR conclusion is correct, running with `--etr_only_wrong`.")
                    raise ValueError("ETR conclusion is correct, but `--etr_only_wrong` is set.")

                # Handle balancing logic
                if args.balance_quadrants:
                    category = (problem_is_erotetic, problem_is_classical)
                    pbar_postfix.update({
                        'EC': balance_counts[(True, True)],    # Erotetic Classical
                        'EN': balance_counts[(True, False)],   # Erotetic Non-classical
                        'NC': balance_counts[(False, True)],   # Non-erotetic Classical
                        'NN': balance_counts[(False, False)],  # Non-erotetic Non-classical
                    })
                elif args.balance_etr_agreement:
                    category = (problem_is_erotetic == problem_is_classical)
                    # print(f"Assessing a problem in category {category}, counts: {balance_counts}")
                    pbar_postfix.update({
                        'Agree': balance_counts[True],     # ETR agrees with classical
                        'Disagree': balance_counts[False], # ETR disagrees with classical
                    })
                else:
                    category = None

                pbar_postfix['T'] = current_counter
                pbar.set_postfix(pbar_postfix)

                # Check atom count constraints
                num_atoms = sum(len(view.logical_form_etr_view.atoms) for view in problem.views)
                if args.num_atoms_set:
                    if num_atoms not in args.num_atoms_set:
                        continue
                    if category is not None:
                        if counts_by_atom[num_atoms][category] >= num_needed_per_category_by_atom:
                            continue
                        counts_by_atom[num_atoms][category] += 1
                    num_atoms_counts[num_atoms] += 1

                # Check category constraints
                if category is not None:
                    if balance_counts[category] >= num_needed_per_category:
                        continue
                    balance_counts[category] += 1

                # print(f"Found problem in category {category}")

                if args.seed_bank == "ILLUSORY_INFERENCE_FROM_DISJUNCTION":
                    n_controls_in_problem_list = len([p for p in problems if str(p.seed_id).startswith("control")])
                    n_targets_in_problem_list = len([p for p in problems if str(p.seed_id).startswith("target")])
                    if str(problem.seed_id).startswith("control") and n_controls_in_problem_list >= n_problems // 2:
                        continue
                    if str(problem.seed_id).startswith("target") and n_targets_in_problem_list >= n_problems // 2:
                        continue

                # Print out the generated problem
                print(f"Generated problem with {num_atoms} atoms. Premises:")
                for v in problem.views:
                    print(" ***", v.logical_form_etr)
                print(f"Conclusion:")
                print(" >>>", conclusion.view.logical_form_etr)
                print(f"Characteristics: erotetic={problem_is_erotetic}, classical={problem_is_classical}")

                problems.append(problem)
                pbar.set_postfix(pbar_postfix)
                break  # Successfully generated a problem, move to next iteration
            except Exception as e:
                print(f"Failed to generate problem: {e}")
                # Get full module path of exception
                exception_key = f"{type(e).__module__}.{type(e).__name__}"
                # Get file and line number where exception occurred
                tb = traceback.extract_tb(e.__traceback__)[-1]  # Get last frame
                location = f"{tb.filename}:{tb.lineno}"
                exception_key = f"{exception_key} at {location}"
                exception_type_counter[exception_key] += 1
                if exception_key not in exception_examples:
                    exception_examples[exception_key] = str(e)[:100]  # Store first 100 chars
                # print("Exception type counts:")
                # for k, v in exception_type_counter.items():
                #     print(f" * {k}: {v}")
                # raise e  # Uncomment to see the exception
                continue  # Try again

    print()
    print("!" * 25, "Error Report", "!" * 25)
    print(f"Succeeded, but overcame these Exceptions:")
    for k, v in exception_type_counter.items():
        print(f" * {v} times: {k}")
        print(f"     Example: {exception_examples[k]}")
    print("!" * 64, "\n")
    
    return problems


def main():
    parser = argparse.ArgumentParser(
        description="Generate a dataset of reasoning problems using ETRCaseGenerator"
    )
    parser.add_argument(
        "-n",
        "--n-problems", 
        type=int,
        default=3,
        help="Number of problems to generate"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument("--num_predicates_per_problem", type=int, default=3, help="Number of predicates to use in each problem. Not used by all generate functions.")
    parser.add_argument("--num_objects_per_problem", type=int, default=3, help="Number of objects to use in each problem. Not used by all generate functions.")
    parser.add_argument("--name_shortening", type=str, default="none", help="How to shorten names of objects and predicates. Options are 'none', 'short', and 'first'.")
    # parser.add_argument("--num_follows", type=int, default=3, help="Number of potential variable assignments which might follow, the top level size of the DNF form of the logical conclusion from the premises.")
    # parser.add_argument("--num_clauses", type=int, default=3, help="A measure of the complexity of the premises.")
    parser.add_argument("--num_pieces", type=int, default=3, help="Number of pieces to use in the premises of each problem. For example, there are for pieces in `(a or b) and (c or d)`.")
    parser.add_argument("--chain_of_thought_prompt", type=str, default="both", help="Whether to include a chain of thought prompt. Options are 'yes', 'no', and 'both'.")
    parser.add_argument("--question_type", type=str, default="all", help="Type of question to ask. Options are 'all', 'yes_no', 'multiple_choice', 'open_ended'.", choices=["all"] + list(get_args(QuestionType)))
    parser.add_argument("--save_file_name", type=str, default="problems", help="Name for saved jsonl files")
    parser.add_argument("--generate_function", type=str, default="random_etr_problem", help="Which function to use in generation.", choices=["random_smt_problem", "random_etr_problem"])
    parser.add_argument("--balance_quadrants", help="Balance the dataset through the 4 quadrants of erotetic and classical yes/no.", action="store_true")
    # TODO(andrew) Implement
    parser.add_argument("--balance_etr_agreement", help="Balance the dataset 50-50 for whether the ETR conclusion is classically correct or not.", action="store_true")
    # TODO(Ryan): Add parameters for problem generation here
    parser.add_argument("--num_atoms_set", nargs="+", type=int, default=[4, 5, 6], help="Set the number of atoms in the problem.")
    parser.add_argument("--generator_max_queue_size", type=int, default=100, help="Maximum number of problems to generate at once, if using the generator with a queue.")
    parser.add_argument("--non_categorical_okay", action="store_true", help="If true, it's okay to generate non-categorical, aka problems whose ETR conclusion has disjunctions in it, or which is null.")
    parser.add_argument("--seed_bank", type=str, default=None, help="Name of the problem seed bank to default to.")
    multi_view_group = parser.add_mutually_exclusive_group(required=False)
    multi_view_group.add_argument("--multi_view", dest="multi_view", action="store_true", help="Generate problems with multiple views")
    multi_view_group.add_argument("--no_multi_view", dest="multi_view", action="store_false", help="Generate problems with a single view")
    parser.set_defaults(multi_view=True)  # Default to True
    parser.add_argument("--no-etr_only_wrong", dest="etr_only_wrong", action="store_false", 
                    help="Allow problems where the ETR conclusion is correct (by default, only wrong ETR conclusions are generated).")
    parser.set_defaults(etr_only_wrong=True)

    args = parser.parse_args()

    if args.question_type == "all":
        question_types = get_args(QuestionType)
    else:
        assert args.question_type in get_args(QuestionType), f"Invalid question type: {args.question_type}, must be in: {get_args(QuestionType)}"
        question_types = [args.question_type]

    set_queue_sizes(args.generator_max_queue_size // 2, args.generator_max_queue_size)

    # Most of the logic occurs here!
    problems: list[FullProblem] = generate_problem_list(n_problems=args.n_problems, args=args, question_types=question_types)

    # Save to file
    for prompt_type in question_types:
        if args.chain_of_thought_prompt == "no" or args.chain_of_thought_prompt == "both":
            fname = f"datasets/{args.save_file_name}_{prompt_type}.jsonl"
            with open(fname, "w") as f:
                for problem in problems:
                    f.write(json.dumps(problem.to_dict_for_jsonl(args, format=prompt_type, chain_of_thought=False)) + "\n")
            print(f"Saved file {fname}")

        if args.chain_of_thought_prompt == "yes" or args.chain_of_thought_prompt == "both":
            fname = f"datasets/{args.save_file_name}_{prompt_type}_with_cot.jsonl"
            with open(fname, "w") as f:
                for problem in problems:
                    f.write(json.dumps(problem.to_dict_for_jsonl(args, format=prompt_type, chain_of_thought=True)) + "\n")
            print(f"Saved file {fname}")

if __name__ == "__main__":
    main()
