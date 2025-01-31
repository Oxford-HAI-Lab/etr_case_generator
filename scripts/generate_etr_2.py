import traceback
import argparse
import json
import math
import random
from typing import get_args
from collections import Counter
from tqdm import tqdm

from etr_case_generator.generator2.etr_generator import set_queue_sizes
from etr_case_generator.generator2.etr_generator2 import ETRGeneratorIndependent
from etr_case_generator.generator2.generate_problem_from_logical import generate_problem
from etr_case_generator.generator2.reified_problem import FullProblem, QuestionType, PartialProblem
from etr_case_generator.generator2.logic_types import AtomCount

from etr_case_generator.ontology import Ontology, get_all_ontologies, natural_name_to_logical_name


def generate_problem_list(n_problems: int, args, question_types: list[str]) -> list[FullProblem]:
    """Generate ETR problems.

    Args:
        n_problems (int): The number of problems to generate
        verbose (bool, optional): Whether to print debugging info. Defaults to False.
    """
    all_ontologies: list[Ontology] = get_all_ontologies()

    for o in all_ontologies:
        o.preferred_name_shortening_scheme = args.name_shortening
        o.fill_mapping()

    quadrant_counts = {
        (True, True): 0,   # (erotetic, classical)
        (True, False): 0,  # (erotetic, non-classical)
        (False, True): 0,  # (non-erotetic, classical)
        (False, False): 0  # (non-erotetic, non-classical)
    }
    num_needed_per_quadrant: int = (n_problems + 3) // 4
    num_needed_per_quadrant_by_atom = num_needed_per_quadrant

    num_atoms_counts = {i : 0 for i in args.num_atoms_set} if args.num_atoms_set else {}
    quadrant_counts_by_atom = {}
    if args.num_atoms_set:
        num_needed_per_quadrant_by_atom = num_needed_per_quadrant // len(args.num_atoms_set)
        print(f"Generating {num_needed_per_quadrant_by_atom} problems per quadrant per atom count.")
        # TODO Refactor this to be less repeated
        for size in args.num_atoms_set:
            quadrant_counts_by_atom[size] = {
                (True, True): 0,   # (erotetic, classical)
                (True, False): 0,  # (erotetic, non-classical)
                (False, True): 0,  # (non-erotetic, classical)
                (False, False): 0  # (non-erotetic, non-classical)
            }

    pbar_postfix = {}

    # This counter will track errors that come up
    exception_type_counter = Counter[str]()

    problem_generator = ETRGeneratorIndependent()
    count_per_size = math.ceil(n_problems / len(args.num_atoms_set)) if args.num_atoms_set else 0
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

                if args.balance:
                    problem_is_erotetic: bool = problem.get_yes_no_conclusion().is_etr_predicted
                    problem_is_classical: bool = problem.get_yes_no_conclusion().is_classically_correct
                    current_quadrant = (problem_is_erotetic, problem_is_classical)

                    # Update the progress bar with current counts
                    pbar_postfix.update({
                        'EC': quadrant_counts[(True, True)],    # Erotetic Classical
                        'EN': quadrant_counts[(True, False)],   # Erotetic Non-classical
                        'NC': quadrant_counts[(False, True)],   # Non-erotetic Classical
                        'NN': quadrant_counts[(False, False)],  # Non-erotetic Non-classical
                        'T': current_counter,                   # Try number
                    })
                    pbar.set_postfix(pbar_postfix)

                    if args.num_atoms_set:
                        num_atoms = sum(len(view.logical_form_etr_view.atoms) for view in problem.views)
                        current_count_by_atom_quadrant = quadrant_counts_by_atom[num_atoms][current_quadrant]
                        if current_count_by_atom_quadrant >= num_needed_per_quadrant:
                            continue
                        quadrant_counts_by_atom[num_atoms][current_quadrant] += 1
                    if quadrant_counts[current_quadrant] >= num_needed_per_quadrant:
                        continue  # Try again if this quadrant is full
                    
                    quadrant_counts[current_quadrant] += 1

                if args.num_atoms_set:
                    num_atoms = sum(len(view.logical_form_etr_view.atoms) for view in problem.views)
                    if num_atoms not in args.num_atoms_set:
                        continue
                    num_atoms_counts[num_atoms] += 1
                
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
                print("Exception type counts:\t", exception_type_counter)
                # traceback.print_exc()
                # raise e
                continue  # Try again

    print(f"Succeeded, but overcame these Exceptions:")
    for k, v in exception_type_counter.items():
        print(f"{k}: {v}")
    
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
    parser.add_argument("--chain_of_thought_prompt", type=str, default="no", help="Whether to include a chain of thought prompt. Options are 'yes', 'no', and 'both'.")
    parser.add_argument("--question_type", type=str, default="all", help="Type of question to ask. Options are 'all', 'yes_no', 'multiple_choice', 'open_ended'.", choices=["all"] + list(get_args(QuestionType)))
    parser.add_argument("--save_file_name", type=str, default="problems", help="Name for saved jsonl files")
    parser.add_argument("--generate_function", type=str, default="random_smt_problem", help="Which function to use in generation.", choices=["random_smt_problem", "random_etr_problem"])
    parser.add_argument("--balance", help="Balance the dataset through the 4 quadrants of erotetic and classical yes/no.", action="store_true")
    # TODO(Ryan): Add parameters for problem generation here
    parser.add_argument("--balance_num_atoms", action="store_true", help="Balance the dataset by number of atoms in the problem.")  # TODO Remove this, just use the set
    parser.add_argument("--num_atoms_set", nargs="+", type=int, help="Set the number of atoms in the problem.")
    parser.add_argument("--generator_max_queue_size", type=int, default=100, help="Maximum number of problems to generate at once.")
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
