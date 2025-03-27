import random
import time
import math

from copy import deepcopy
from dataclasses import dataclass, field

from pyparsing import ParseException

from etr_case_generator.logic_types import AtomCount
from etr_case_generator.reified_problem import PartialProblem, ReifiedView
from etr_case_generator.seed_problems import (
    create_starting_problems,
)
from etr_case_generator.study_replication_seed_problems import (
    ILLUSORY_INFERENCE_FROM_DISJUNCTION_REVERSE_PREMISES_TEST,
    ILLUSORY_INFERENCES_WITH_QUANTIFIERS,
    ILLUSORY_INFERENCE_FROM_DISJUNCTION,
)
from etr_case_generator.mutations import get_view_mutations
from etr_case_generator.ontology import Ontology
from pyetr import View
from pyetr.cases import BaseExample
from pyetr.inference import default_inference_procedure
from typing import Optional, Generator, Tuple, Set, Counter, List, Callable

from etr_case_generator.view_to_natural_language import view_to_natural_language
from etr_case_generator.mutations import get_random_view
from pyetr.inference import default_inference_procedure

# HELPER FUNCTIONS

def count_atoms_in_problem(problem: PartialProblem) -> int:
    """Count total number of atoms in a problem's premises."""
    if not problem.premises:
        return 0
    return sum(
        len(premise.logical_form_etr_view.atoms)
        for premise in problem.premises
        if premise.logical_form_etr_view
    )


def get_atom_count_distribution(problems: List[PartialProblem]) -> tuple[Counter[AtomCount], float]:
    """Get distribution of atom counts across a list of problems and the median frequency.

    Returns:
        tuple[Counter[AtomCount], float]: A tuple containing:
            - Counter mapping atom counts to their frequencies
            - The median frequency (0.0 if no problems)
    """
    counts = Counter[AtomCount]()
    for problem in problems:
        count = AtomCount(count_atoms_in_problem(problem))
        counts[count] += 1

    # Calculate median frequency
    frequencies = sorted(counts.values())
    median_freq = frequencies[len(frequencies) // 2] if frequencies else 0.0

    return counts, median_freq

def create_partial_problem(views: Tuple[View], seed_problem_id: str) -> PartialProblem:
    premises: list[ReifiedView] = []
    for p in views:
        premises.append(
            ReifiedView(
                logical_form_etr_view=p,
                # Generator is not responsible for generating English forms,
                # since it's agnostic to the ontology
                english_form=None,
            )
        )
    etr_what_follows = default_inference_procedure(views)
    new_problem = PartialProblem(
        premises=premises,
        possible_conclusions_from_logical=None,
        possible_conclusions_from_etr=None,
        etr_what_follows=ReifiedView(
            logical_form_etr_view=etr_what_follows,
            # Generator is not responsible for generating English forms,
            # since it's agnostic to the ontology
            english_form=None,
        ),
        seed_id=seed_problem_id,
    )
    return new_problem

def is_categorical_only(partial_problem: PartialProblem) -> bool:
    """Check if a partial problem is categorical."""
    views = [p.logical_form_etr_view for p in partial_problem.premises]
    conclusion = default_inference_procedure(views)
    return len(conclusion.stage) == 1 and not conclusion.is_verum

# GENERATOR CLASS

class ETRGeneratorIndependent:
    already_generated: Set[str]  # Used to prevent duplicate problems. str(PartialProblem) is used as key.

    def __init__(self, seed_bank: Optional[str] = None):
        self.already_generated = set()
        self.count_of_atom_counts_generated = Counter[AtomCount]()  # For logging

        self.seed_bank = seed_bank

    def generate_multi_view_problem(self, needed_counts: Counter[AtomCount], categorical_only: bool=True) -> PartialProblem:
        """Generate a problem with multiple views that meets the specified atom count requirements.
        
        Args:
            needed_counts: Counter specifying how many problems of each atom count are needed
            categorical_only: If True, only return problems with categorical conclusions
            
        Returns:
            A PartialProblem with multiple views that meets the requirements
            
        Raises:
            ValueError: If unable to generate a valid problem after max_attempts
        """
        max_attempts = 10
        for attempt in range(max_attempts):
            # Start with an empty list of views
            views = []

            # Start with a random view
            views.append(get_random_view())
            
            # Try to build a valid problem by adding views incrementally
            max_attempts_to_add_new_view = 10
            for _ in range(max_attempts_to_add_new_view):
                # 1. Get a random view using mutations.get_random_view()
                random_view = get_random_view()

                # 2. Check if adding this view results in a valid erotetic conclusion
                temp_views = views + [random_view]

                try:
                    # Use ETR's inference procedure to check if a conclusion follows
                    conclusion = default_inference_procedure(temp_views)

                    # If conclusion is null (verum), try a different view
                    if conclusion.is_verum:
                        continue  # Try a different continuation
                except Exception as e:
                    # If there's an error in inference, try a different view
                    print(f"Error in inference: {e}")
                    continue

                # 3. Add the view since it produces a valid conclusion
                views.append(random_view)

                # 4. Check if the current problem meets our requirements, and emit it if so
                current_atom_count = sum(len(view.atoms) for view in views)
                if AtomCount(current_atom_count) in needed_counts and needed_counts[AtomCount(current_atom_count)] > 0:
                    # Check if the conclusion is categorical (if required)
                    conclusion = default_inference_procedure(views)
                    is_categorical = len(conclusion.stage) == 1 and not conclusion.is_verum

                    if not categorical_only or is_categorical:
                        # We found a valid problem that meets our requirements

                        return create_partial_problem(tuple(views), "no_seed")
                
                # 5. If we've exceeded all possible atom counts, backtrack
                if all(current_atom_count > count for count in needed_counts.keys()):
                    # Remove the last few views and try again with different ones
                    # print(f"Backtracking from {current_atom_count} atoms, {len(views)} views")
                    backtrack_count = min(3, len(views))
                    if backtrack_count > 0:
                        views = views[:-backtrack_count]

        # If we failed to generate a novel problem with desired count
        raise ValueError(f"Failed to generate problem with desired atom count after {max_attempts} attempts")

    def generate_problem(self, needed_counts: Counter[AtomCount], categorical_only: bool=True, multi_view: bool=False) -> PartialProblem:
        """
        Generate a single ETR problem.

        This function works as follows:
        - Choose a random seed problem from the list in seed_problems.py
        - Choose an atom count from the needed_counts distribution
        - Repeatedly mutate the seed problem until it has the desired atom count
        - Check if the problem has already been generated, and if so, repeat the process
        - Return the generated problem
        
        Args:
            needed_counts: Counter specifying how many problems of each atom count are needed
            categorical_only: If True, only return problems with categorical conclusions
            multi_view: If True, generate a problem with multiple views instead of mutating a seed problem
        """
        if multi_view:
            return self.generate_multi_view_problem(needed_counts, categorical_only)

        # print(f"Categorical only: {categorical_only}")
        max_attempts = 10
        for attempt in range(max_attempts):
            # Choose random seed problem
            if self.seed_bank:
                # Try to access the seed problems from the specified seed bank
                try:
                    seed_bank_problems = locals()[self.seed_bank]
                except:
                    raise ValueError(f"Invalid seed bank: {self.seed_bank}")
                seed_problem: PartialProblem = random.choice(seed_bank_problems)
                return deepcopy(seed_problem)

            seed_problem: PartialProblem = random.choice(create_starting_problems())
            
            # Choose target atom count from needed_counts
            possible_counts = [count for count, needed in needed_counts.items() if needed > 0]
            if not possible_counts:
                raise ValueError("No more problems needed for any atom count")
                
            target_count = random.choice(possible_counts)
            current_problem: PartialProblem = seed_problem

            # Try up to 200 sequential mutations to reach target count
            mutation_attempts = 200
            for mut_count in range(mutation_attempts):
                current_count = AtomCount(count_atoms_in_problem(current_problem))

                # print(f"Problem currently has this many premises: {current_count}, trying to get to {target_count}")
                if current_count > target_count + 2:
                    # Oops, try again
                    # print(f"Too many atoms, retrying -- 2")
                    break
                
                if current_count == target_count:
                    # Check if we've generated this exact problem before
                    problem_key = str(current_problem)
                    if problem_key in self.already_generated and self.seed_bank is None:
                        print(f"Already generated this problem, retrying")
                        # Keep going with mutations, to try to get a novel problem
                    else:
                        problem_is_categorical = is_categorical_only(current_problem)
                        current_problem.etr_predicted_conclusion_is_categorical = (
                            problem_is_categorical
                        )
                        if categorical_only and not problem_is_categorical:
                            print(f"Problem is not categorical, retrying")
                        elif categorical_only and problem_is_categorical:
                            print(f"Found a categorical problem yay!")
                        if (not categorical_only) or problem_is_categorical:
                            self.already_generated.add(problem_key)
                            self.count_of_atom_counts_generated[current_count] += 1

                            # Stats on what we've already generated
                            # print(f"Generated atom counts:", {k: self.count_of_atom_counts_generated[k] for k in sorted(self.count_of_atom_counts_generated.keys())})

                            return current_problem
                
                # Randomly choose a premise to mutate
                if len(current_problem.premises) == 1:
                    premise_idx = 0
                else:
                    # Try to keep the last premise unchanged
                    premise_idx = random.randrange(len(current_problem.premises) - 1)
                view = current_problem.premises[premise_idx]
                
                # Decide whether to try to increase atoms or allow any mutation
                if random.random() < 0.5:  # Sometimes mutate sideways
                    only_increase = False
                elif current_count >= target_count:  # Don't grow if we're already over
                    only_increase = False
                else:
                    only_increase = current_count < target_count
                    
                # Get a single mutation
                try:
                    mutations = get_view_mutations(view.logical_form_etr_view,
                                                only_increase=only_increase,
                                                only_do_one=True)
                    if not mutations or len(mutations) != 1:
                        print(f"Expected exactly one mutation, got {len(mutations)}")
                        print(f"Seed id: {seed_problem.seed_id}")
                        print("View:", view.logical_form_etr_view)
                        print("Current Problem:", current_problem)
                        raise ValueError("Expected exactly one mutation")

                    # Apply the mutation to create new problem
                    mut = next(iter(mutations))  # Get the single mutation
                    new_premises: Tuple[ReifiedView] = (
                        current_problem.premises[:premise_idx] +
                        [ReifiedView(logical_form_etr_view=mut)] +
                        current_problem.premises[premise_idx+1:]
                    )
                    base_views = [p.logical_form_etr_view for p in new_premises]

                    # Update current problem for next iteration
                    current_problem = create_partial_problem(base_views, seed_problem.seed_id)
                except ParseException as e:
                    print(f"Failed to mutate problem: {e}, retrying")
                    raise e
                    # continue

        # If we failed to generate a novel problem with desired count
        raise ValueError(f"Failed to generate problem with desired atom count after {max_attempts} attempts")
