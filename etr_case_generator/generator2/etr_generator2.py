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
    already_generated: Set[PartialProblem]  # Used to prevent duplicate problems

    def __init__(self):
        pass

    def generate_problem(self, needed_counts: Counter[AtomCount] = None) -> PartialProblem:
        """
        Generate a single ETR problem.

        This function works as follows:
        - Choose a random seed problem from the list in seed_problems.py
        - Choose an atom count from the needed_counts distribution
        - Repeatedly mutate the seed problem until it has the desired atom count
        - Check if the problem has already been generated, and if so, repeat the process
        - Return the generated problem
        """
        raise NotImplementedError

