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

# Generation Parameters
UNDER_REPRESENTED_SEED_BOOST = 3.0
ATOMS_PER_PROBLEM_BOOST = 5.0
OVERUSED_ATOM_COUNT_DEMERIT = 8.0
SOFTMAX_TEMPERATURE = 2.0

def count_atoms_in_problem(problem: PartialProblem) -> int:
    """Count total number of atoms in a problem's premises."""
    if not problem.premises:
        return 0
    return sum(
        len(premise.logical_form_etr_view.atoms)
        for premise in problem.premises 
        if premise.logical_form_etr_view
    )

def get_atom_count_distribution(problems: List[PartialProblem]) -> tuple[Counter[int], float]:
    """Get distribution of atom counts across a list of problems and the median frequency.
    
    Returns:
        tuple[Counter[int], float]: A tuple containing:
            - Counter mapping atom counts to their frequencies
            - The median frequency (0.0 if no problems)
    """
    counts = Counter[int]()
    for problem in problems:
        counts[count_atoms_in_problem(problem)] += 1
    
    # Calculate median frequency
    frequencies = sorted(counts.values())
    median_freq = frequencies[len(frequencies)//2] if frequencies else 0.0
    
    return counts, median_freq

def boost_low_num_atom_problems(problem: PartialProblem, all_problems: List[PartialProblem]) -> float:
    """
    A helper function to bias generation towards problems with fewer atoms. It first counts the number of atoms in all the problems, and then boosts the problem if it has fewer atoms than the average.
    
    Args:
        problem: The problem to calculate the boost for
        all_problems: List of all problems in the queue for comparison
        
    Returns:
        float: A boost multiplier, where values > 1.0 increase selection probability
    """
    if not problem.premises or not all_problems:
        return 1.0
        
    # Count atoms in the target problem
    problem_atoms = problem.num_atoms()
    
    # Calculate average atoms across all problems
    total_atoms = 0
    valid_problems = 0
    for p in all_problems:
        if p.premises:
            atoms = p.num_atoms()
            total_atoms += atoms
            valid_problems += 1
            
    if valid_problems == 0:
        return 1.0
        
    avg_atoms = total_atoms / valid_problems
    
    # Boost problems with fewer than average atoms
    if problem_atoms < avg_atoms:
        max_boost = ATOMS_PER_PROBLEM_BOOST
        percent_less = (avg_atoms - problem_atoms) / avg_atoms
        return 1.0 + max_boost * percent_less
    return 1.0

@dataclass
class ETRGenerator:
    """Maintains the state of the ETR problem generator between calls."""
    problem_set: List[PartialProblem] = field(default_factory=list)
    # Queue sizes are OVERRIDDEN in generate_etr_2.py
    min_queue_size: int = 50  # Minimum number of problems to maintain in queue
    max_queue_size: int = 100  # Maximum size of the queue. This should be large relative to max_mutations_per_base_problem to maintain diversity
    max_queue_size_init: int = None
    _generator: Optional[Generator[PartialProblem, None, None]] = None
    max_mutations_per_base_problem: int = 20  # Maximum number of mutations per base problem

    seed_ids_yielded: Counter[str] = field(default_factory=Counter)  # To help maintain diversity

    generation_bias_function: Optional[Callable[[PartialProblem, List[PartialProblem]], float]] = None  # Bias generation toward certain types of problem, output is softmaxed
    softmax_temperature: float = SOFTMAX_TEMPERATURE  # Temperature for softmax function
    unused_seed_boost: float = UNDER_REPRESENTED_SEED_BOOST  # Boost for seed ids that have not been used as much yet
    overused_atom_count_demerit: float = OVERUSED_ATOM_COUNT_DEMERIT  # Boost for problems with fewer atoms than average

    filtering_fn: Optional[Callable[[PartialProblem], bool]] = None  # Optional filter function for problems

    needed_counts: Counter[AtomCount] = None  # Atom counts needed for the queue

    def initialize_generator(self) -> None:
        """Initialize the problem generator."""
        self._generator = self._generate_problems()

        # Fill the queue with initial problems
        self.problem_set.extend(create_starting_problems())

        self.max_queue_size_init = self.max_queue_size

        if self.max_queue_size < self.max_mutations_per_base_problem * 5:
            print("Warning: max_queue_size is less than 5 times max_mutations_per_base_problem. This may lead to a lack of diversity during sampling.")

    def get_from_queue_for_mutations(self):
        """Select a problem from the queue using softmax-weighted random selection.
        
        The selection probability is influenced by:
        1. The generation_bias_function if provided
        2. A boost for previously unused seed_ids
        3. Temperature scaling for the softmax
        
        Returns:
            PartialProblem: The selected problem for mutation
        """
        if not self.problem_set:
            raise ValueError("Cannot select from empty problem set")
            
        def calculate_score(problem: PartialProblem, all_problems: List[PartialProblem]) -> float:
            """Calculate selection score for a problem."""
            # Start with a positive base score for softmax
            score = 1.0
            
            # Add generation bias if function provided
            if self.generation_bias_function is not None:
                score += self.generation_bias_function(problem, all_problems) - 1.0  # TODO Why -1 here?
                
            # Add boost for underrepresented seeds
            if self.seed_ids_yielded:
                avg_uses = sum(self.seed_ids_yielded.values()) / len(self.seed_ids_yielded)
                current_uses = self.seed_ids_yielded[problem.seed_id]
                if current_uses < avg_uses:
                    # Calculate boost proportional to how underrepresented this seed is
                    boost_factor = (avg_uses - current_uses) / avg_uses
                    score += self.unused_seed_boost * boost_factor

            # Add boost for underrepresented atom counts
            problem_atom_counts, median_freq = get_atom_count_distribution(all_problems)
            current_atoms = count_atoms_in_problem(problem)
            # Add large negative if this problem has more atoms than the median
            if problem_atom_counts[current_atoms] > median_freq:
                score -= self.overused_atom_count_demerit

            return score
            
        # Calculate scores for each problem
        scores = [calculate_score(p, self.problem_set) for p in self.problem_set]
            
        # Apply softmax with temperature
        exp_scores = [
            math.exp(score / self.softmax_temperature) 
            for score in scores
        ]
        total = sum(exp_scores)
        probabilities = [score / total for score in exp_scores]
        
        # Select problem based on calculated probabilities
        return random.choices(
            self.problem_set,
            weights=probabilities,
            k=1
        )[0]

    def get_mutated_premises(self, problem: PartialProblem) -> Set[Tuple[View, ...]]:
        """
        Get all possible mutations of the premises of a problem.
        
        Returns:
            Set[List[View]]: A set of all possible mutated premises
        """
        mutations = set()
        assert problem.premises is not None
        for i, view in enumerate(problem.premises):
            assert view.logical_form_etr_view is not None
            for mut in get_view_mutations(view.logical_form_etr_view, only_increase=True):
                new_mutation = (
                    tuple([p.logical_form_etr_view for p in problem.premises[:i]]) +
                    (mut,) +
                    tuple([p.logical_form_etr_view for p in problem.premises[i+1:]])
                )
                mutations.add(new_mutation)
        # Add a mutation where we add a new premise
        mutations.add(
            tuple([p.logical_form_etr_view for p in problem.premises]) +
            (View.from_str("{A(a())}"),)
        )

        # Add a mutation where we remove a random premise

        return mutations

    def get_some_good_mutations(self, mutations: Set[Tuple[View, ...]]):
        """The purpose of this function is to promote diversity in the size of problems that are generated by the mutations process."""
        definitely_good_mutations = []
        other_mutations = []

        # Get distribution of atom counts across problems
        problem_atom_counts, median_freq = get_atom_count_distribution(self.problem_set)

        for mutation in mutations:
            num_atoms = sum(len(view.atoms) for view in mutation)
            
            # Check if this mutation's atom count occurs less often than the median
            under_represented_num_atoms = problem_atom_counts[num_atoms] < median_freq

            if under_represented_num_atoms:
                definitely_good_mutations.append(mutation)
            else:
                other_mutations.append(mutation)

        print(f"Found {len(definitely_good_mutations)} under-represented mutations out of {len(mutations)} total mutations")
        print("Atom counts in problem_set:", {k: problem_atom_counts[k] for k in sorted(problem_atom_counts.keys())})

        random.shuffle(definitely_good_mutations)
        random.shuffle(other_mutations)
        mutations = definitely_good_mutations + other_mutations
        return mutations[:self.max_mutations_per_base_problem]

    def _generate_problems(self) -> Generator[PartialProblem, None, None]:
        """Internal generator function that creates new problems."""
        # # First, try to create a starting problem
        # seed_problem = self.create_starting_problems()

        # # Add the seed problem to the queue
        # yield seed_problem

        mutation_count = 0
        while True:
            # TODO Consider iterating through this data structure in a more chaotic way than
            # just queueing stuff (priority queue, randomizing at each step, etc.)
            # Get the most recent problem from the queue to mutate
            if not self.problem_set:
                print(f"Queue is empty after {mutation_count} mutations")
                # If queue is empty, we've exhausted this line of problems
                raise StopIteration("Queue is empty")

            # Another way to bias generation is to pick a problem from the queue that is
            # e.g. "largest" -> (then you can also think about just mutating by adding
            # or removing premises if you want to "bias" the walk in a certain direction)
            base_problem = self.get_from_queue_for_mutations()  # Look at a problem without removing it
            # print(f"Chose base problem with seed id {base_problem.seed_id}")

            possible_mutations: Set[Tuple[View, ...]] = self.get_mutated_premises(base_problem)
            print(f"Selecting new base problem with id {base_problem.seed_id} and atom count {count_atoms_in_problem(base_problem)}", f"Applying {self.max_mutations_per_base_problem} out of {len(possible_mutations)} mutations to base problem")

            # Randomly select a subset of the mutations to apply
            used_mutations = self.get_some_good_mutations(possible_mutations)

            # Sanity check: everything in possible_mutations should have the same number
            # of premises as base_problem EXCEPT one (which has n+1 premises)
            for mutated_premises in used_mutations:
                etr_what_follows = default_inference_procedure(mutated_premises)
                premises = []
                for p in mutated_premises:
                    premises.append(
                        ReifiedView(
                            logical_form_etr_view=p,
                            # Generator is not responsible for generating English forms,
                            # since it's agnostic to the ontology
                            english_form=None,
                        )
                    )
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
                    seed_id=base_problem.seed_id,
                )
                # print("-" * 80)
                # print("New problem with seed id:", new_problem.seed_id)
                self.seed_ids_yielded[base_problem.seed_id] += 1
                yield new_problem

            mutation_count += 1

    def ensure_queue_filled(self) -> None:
        """Ensure the queue has at least min_queue_size problems."""
        if self._generator is None:
            self.initialize_generator()

        if len(self.problem_set) < self.min_queue_size:
            print(f"Queue has {len(self.problem_set)} problems, filling to {self.max_queue_size}")
            current_time = time.time()
            while len(self.problem_set) < self.max_queue_size:
                assert self._generator is not None
                new_problem = next(self._generator)
                self.problem_set.append(new_problem)
            print(f"Filled queue to size {len(self.problem_set)} in {time.time() - current_time:.2f} seconds")

        # Statistics on the new queue
        num_atoms_count, median_freq = get_atom_count_distribution(self.problem_set)
        # print("Atom count in new queue:", {k: num_atoms_count[k] for k in sorted(num_atoms_count.keys())})
        # print(f"Median frequency: {median_freq}")

    # TODO: this could be passed an optional vocab_size, filter the list of problems
    # to match
    # If there isn't one, try to generate until you get one
    def get_next_problem(self, filter_fn: Optional[Callable[[PartialProblem], bool]] = None) -> PartialProblem:
        """Get the next problem from the queue that matches the filter, generating more if needed.
        
        Args:
            filter_fn: Optional function that takes a PartialProblem and returns bool.
                      If provided, only problems that pass this filter will be considered.
                      Defaults to None (no filtering).
        
        Returns:
            A randomly selected problem that passes the filter.
            
        Raises:
            RuntimeError: If no problems match the filter after filling the queue.
        """
        self.ensure_queue_filled()

        # If no filter provided, use a function that accepts everything
        has_filter = filter_fn is not None
        if filter_fn is None:
            filter_fn = lambda _: True

        self.filtering_fn = filter_fn

        # Get indices of all problems that pass the filter
        valid_indices = [i for i, p in enumerate(self.problem_set) if filter_fn(p)]
        print(f"Found {len(valid_indices)} problems that match the filter ({has_filter})")

        if not valid_indices:
            # Temporarily increase the queue size to try to find a problem that matches the filter
            self.max_queue_size += self.max_queue_size_init
            self.min_queue_size = self.max_queue_size + 1
            print(f"Increasing queue size to {self.max_queue_size} to attempt to find a problem that matches the filter")

            # Print atom stats
            num_atoms_count, _ = get_atom_count_distribution(self.problem_set)
            print("Atom count in queue:", {k: num_atoms_count[k] for k in sorted(num_atoms_count.keys())})

            self.ensure_queue_filled()
            valid_indices = [i for i, p in enumerate(self.problem_set) if filter_fn(p)]
        
        if not valid_indices:
            raise RuntimeError("No problems match the provided filter criteria")
            
        # Select random valid index and remove that problem
        if len(valid_indices) <= 1:
            print(f"Warning, only {len(valid_indices)} valid problem found")
        idx = random.choice(valid_indices)
        return self.problem_set.pop(idx)

# Global state instance
_etr_generator = ETRGenerator()

def random_etr_problem(filter_fn: Optional[Callable[[PartialProblem], bool]] = None,
                       bias_function: Optional[Callable[[PartialProblem, List[PartialProblem]], float]] = None,
                       needed_counts: Counter[AtomCount] = None) -> PartialProblem:
    """
    Generate a random ETR problem that matches the filter criteria.
    
    Args:
        filter_fn: Optional function that takes a PartialProblem and returns bool.
                  If provided, only problems that pass this filter will be returned.
                  Defaults to None (no filtering).
        bias_function: Optional function that takes a PartialProblem and a list of all problems
                       and returns a float. This function can be used to bias the generation
                       towards certain types of problems. Defaults to None.

    Side Effect:
        Updates the global generator state and sets the generation bias function
        
    Returns:
        A new PartialProblem instance that passes the filter
        
    Raises:
        RuntimeError: If no problems match the filter criteria
    """
    if bias_function is not None:
        _etr_generator.generation_bias_function = bias_function
    if needed_counts is not None:
        _etr_generator.needed_counts = needed_counts

    problem = _etr_generator.get_next_problem(filter_fn)
    return problem

def reset_generator_state():
    """Reset the generator state to initial conditions."""
    global _etr_generator
    _etr_generator = ETRGenerator()

def set_queue_sizes(min_size: int, max_size: int):
    """Configure the queue size parameters."""
    if min_size > max_size:
        raise ValueError("min_size must be less than or equal to max_size")
    _etr_generator.min_queue_size = min_size
    _etr_generator.max_queue_size = max_size

def set_max_mutations(max_mutations: int):
    """Set the maximum number of mutations before considering a line exhausted."""
    if max_mutations <= 0:
        raise ValueError("max_mutations must be positive")
    _etr_generator.max_mutations = max_mutations

def get_queue_size() -> int:
    """Get the current size of the problem queue."""
    return len(_etr_generator.problem_set)
