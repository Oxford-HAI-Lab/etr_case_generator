import random
import time
import math

from dataclasses import dataclass, field

from etr_case_generator.generator2.logic_types import AtomCount
from etr_case_generator.generator2.reified_problem import PartialProblem, ReifiedView
from etr_case_generator.generator2.seed_problems import create_starting_problems
from etr_case_generator.mutations import get_view_mutations
from etr_case_generator.ontology import Ontology
from pyetr import View
from pyetr.cases import BaseExample
from pyetr.inference import default_inference_procedure
from typing import Optional, Generator, Tuple, Set, Counter, List, Callable

from etr_case_generator.view_to_natural_language import view_to_natural_language

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

# GENERATOR CLASS

class ETRGeneratorIndependent:
    already_generated: Set[str]  # Used to prevent duplicate problems. str(PartialProblem) is used as key.

    def __init__(self):
        self.already_generated = set()

    def generate_problem(self, needed_counts: Counter[AtomCount]) -> PartialProblem:
        """
        Generate a single ETR problem.

        This function works as follows:
        - Choose a random seed problem from the list in seed_problems.py
        - Choose an atom count from the needed_counts distribution
        - Repeatedly mutate the seed problem until it has the desired atom count
        - Check if the problem has already been generated, and if so, repeat the process
        - Return the generated problem
        """
        max_attempts = 10
        for attempt in range(max_attempts):
            # Choose random seed problem
            seed_problem = random.choice(create_starting_problems())
            
            # Choose target atom count from needed_counts
            possible_counts = [count for count, needed in needed_counts.items() if needed > 0]
            if not possible_counts:
                raise ValueError("No more problems needed for any atom count")
                
            target_count = random.choice(possible_counts)
            current_problem = seed_problem

            # Try up to 200 sequential mutations to reach target count
            mutation_attempts = 200
            for mut_count in range(mutation_attempts):
                current_count = AtomCount(count_atoms_in_problem(current_problem))
                
                if current_count == target_count:
                    # Check if we've generated this exact problem before
                    problem_key = str(current_problem)
                    if problem_key not in self.already_generated:
                        self.already_generated.add(problem_key)
                        return current_problem
                    # Keep going with mutations, to try to get a novel problem
                
                # Randomly choose a premise to mutate
                if len(current_problem.premises) == 1:
                    premise_idx = 0
                else:
                    # Try to keep the last premise unchanged
                    premise_idx = random.randrange(len(current_problem.premises) - 1)
                view = current_problem.premises[premise_idx]
                
                # Decide whether to try to increase atoms or allow any mutation
                if random.random() < 0.5:
                    only_increase = False
                else:
                    only_increase = current_count < target_count
                    
                # Get a single mutation
                mutations = get_view_mutations(view.logical_form_etr_view, 
                                            only_increase=only_increase, 
                                            only_do_one=True)
                assert len(mutations) == 1, f"Expected exactly one mutation, got {len(mutations)}"
                    
                # Apply the mutation to create new problem
                mut = next(iter(mutations))  # Get the single mutation
                new_premises = (
                    current_problem.premises[:premise_idx] + 
                    [ReifiedView(logical_form_etr_view=mut)] +
                    current_problem.premises[premise_idx+1:]
                )
                
                # Update current problem for next iteration
                current_problem = PartialProblem(
                    premises=list(new_premises),
                    seed_id=current_problem.seed_id
                )

        # If we failed to generate a novel problem with desired count
        raise ValueError(f"Failed to generate problem with desired atom count after {max_attempts} attempts")

