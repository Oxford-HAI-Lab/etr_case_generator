# etr_case_generator

Welcome! `etr_case_generator` is a generation tool for producing datasets of reasoning problems. These problems are constructed to test the [Erotetic Theory of Reasoning](https://academic.oup.com/book/45443), though they can be used to assess general soundness in predicate reasoning, and are largely tailored for prompting LLMs.

This system utilises ETR's predicate calculus with the [`PyETR`](https://github.com/Oxford-HAI-Lab/PyETR) package. For now, we do not use the extensions for probabilistic reasoning and decision-making.

## Setup

`etr_case_generator` works with Python 3.12.5 and may work with other versions. Here, mileage may vary, but one might do this with:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Then, install requirements:

```bash
pip install -r requirements.txt
```

Next, install the PySMT z3 solver:
```bash
pysmt-install --z3
```

For local development, this package should be installed in editable mode:
```bash
pip install -e .
```

## Usage

### Generating Whole Reasoning Problems

To get started with the generator, try this call to the `generate_etr.py` script:

```bash
python -m scripts.generate_etr --save_file_name dev --question_type=all --generate_function=random_etr_problem -n 10
```

This will generate 10 problems and save them to files like `datasets/dev_*.jsonl`:
```
Saved file datasets/dev_yes_no.jsonl
Saved file datasets/dev_yes_no_with_cot.jsonl
Saved file datasets/dev_multiple_choice.jsonl
Saved file datasets/dev_multiple_choice_with_cot.jsonl
Saved file datasets/dev_open_ended.jsonl
Saved file datasets/dev_open_ended_with_cot.jsonl
```

See the [lm_eval documentation](lm_eval/tasks/README.md) for more information on how to use this dataset with lm_eval.

### Inspecting the Dataset

You can use the `pprint_problems` script to inspect the dataset:

- To show the details of 1 random problem:
```bash
pprint_problems datasets/dev_yes_no.jsonl -n 1 -r
```

- To show the structure of the dataset:
```bash
pprint_problems datasets/dev_yes_no.jsonl --structure
```

- To look at just the question, premises, and conclusion for 3 random problems:
```bash
pprint_problems datasets/dev_yes_no.jsonl -n 3 -r --parts question scoring_guide/premises scoring_guide/question_conclusion
```

- To show stats about the dataset:
```bash
pprint_problems datasets/dev_yes_no.jsonl -p scoring_guide/etr_answer scoring_guide/logically_correct_answer --stats --full_combinatoric
```

## Details of Problem Generation

### High-level Summary

The problem generation process is based on a randomized depth-first search for a list of `View` objects which will form the premises of a problem.
The search incrementally chooses a random `View` object to append to the list, by means of randomly applying mutations to a random 'seed problem' and filtering for Views which keep the ETR-derived conclusion of the problem non-trivial.
New `View` objects are incrementally added until the sum of the atom counts across the list is equal to one of a specified set of counts, representing a desired degree of complexity.
If the greatest permitted atom count is exceeded, the last few `View` objects are backtracked.
After too many failed attempts, the entire list is discarded and we start from scratch.

There are some other filtering steps which may be tuned.
When using `generate_etr.py`, by default the problem is required to have a 'categorical' conclusion under ETR, (meaning the `View` amounts to a conjunction of atoms without any disjunctions).
This check intervenes during the depth-first search, causing the search to continue if the condition is not met.
The script `generate_etr.py` applies further logic to filter the generated problems, by default this is used to restrict to problems that have logically fallacious ETR-predicated conclusions.

### Generating Views and Mutations

The `etr_case_generator.etr_generator_no_queue` module exposes a class called
`ETRGeneratorIndependent` that we use for generating reasoning problems.

The `generate_etr.py` script from above was our entrypoint to the
`ETRGeneratorIndependent` class. By default, `generate_etr.py` sets the `multi_view`
argument to be true, meaning our problems are constructed using the
`ETRGeneratorIndependent.generate_multi_view_problem` function. This function
iteratively constructs problems using the `mutations.get_random_view` function, which,
at its core, selects random views from `ALL_SEED_PROBLEMS` and mutates them according to
the `mutations.get_view_mutations` function. These objects—the original views from the
problems in `ALL_SEED_PROBLEMS`, and the mutation logic in
`get_view_mutations`—characterise our search space for new reasoning problems.

`ALL_SEED_PROBLEMS`, defined in `mutations.py`, begins an initial bank of possible
`View`s to select by combining `create_starting_problems` and the
`ILLUSORY_INFERENCE_FROM_DISJUNCTION` seed problems. `create_starting_problems` is a
function defined in `etr_case_generator/seed_problems.py`, and contains some hardcoded
problems corresponding to examples from the
[*Reason and Inquiry*](https://academic.oup.com/book/45443) text.
`ILLUSORY_INFERENCE_FROM_DISJUNCTION` contains templates for control and target
problems for the original study on illusory inferences from disjunctions. Note that the composition of `ALL_SEED_PROBLEMS` can be easily extended by either appending manually to `create_starting_problems` or by adding other seed banks from the `study_replication_seed_problems.py` file.

The `mutations.get_view_mutations` function can change the structure of a given `View` object
in a couple of basic ways:
1. The given `View` can have a new predicate atom conjoined to an existing `State`, in either the stage or supposition.
2. The given `View` can have a new predicate atom disjoined into the stage or supposition, creating a new `State` in that set of `State`s.
3. 1 or 2 can occur with an existing predicate atom already in the `View`.
4. An existing constant can be replaced with an arbitrary object that is either universally or existentially quantified (currently, up to a maximum depth of 3).
5. A random atom can be taken to be at issue, or not at issue.
6. A random atom can be negated.

N.B. here—our system restricts its representations to unary predicates in all cases. This means that currently, you can have "the dog is fluffy," but not "the dog is between home and the park."

### Filtering

There are several conditions by which problems can be filtered which can be set using arguments passed to `generate_etr.py`.
As mentioned above, the default behaviour is to filter for problems with a categorical ETR-predicted solution.
This is disabled by passing the commandline argument `--non_categorical_okay` to `generate_etr.py`.
Unlike other filters, the logic for this task is embedded in the function `ETRGeneratorIndependent.generate_multi_view_problem`, i.e. the main search loop, where it is controlled by the Boolean `categorical_only` argument.

The function `generate_problem_list` in `generate_etr.py` directly handles the logic for filtering problems after they have been generated in order to balance between those with correct and those with fallacious ETR-predicted conclusions.
As mentioned, the default behaviour is to pass through only those with fallacious ETR-predicted conclusions.