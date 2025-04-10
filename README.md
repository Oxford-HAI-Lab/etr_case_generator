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

## Generation

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

You can use the `pprint_problems` script to inspect the dataset. 

```bash
pip install pprint_problems
```

Then, here are some ways you can inspect it.

Show the details of 1 random problems:

```bash
pprint_problems datasets/dev_yes_no.jsonl -n 1 -r
```

Show the structure of the dataset:

```bash
pprint_problems datasets/dev_yes_no.jsonl --structure
```

Look at just the question, premises, and conclusion for 3 random problems:

```bash
pprint_problems datasets/dev_yes_no.jsonl -n 3 -r --parts question scoring_guide/premises scoring_guide/question_conclusion
```

Show stats about the dataset:

```bash
pprint_problems datasets/dev_yes_no.jsonl -p scoring_guide/etr_answer scoring_guide/logically_correct_answer --stats --full_combinatoric
```

### Generating Individual Views

The `etr_case_generator.generator` module exposes a class called `ETRCaseGenerator`,
which is designed for generating either individual `pyetr.View` objects or entire
reasoning problems.

`ETRCaseGenerator.generate_view` returns a single random view with some configurable
number of disjunctions, conjuncts, and a configurable rate of randomly negated atoms. In
addition, you can specify whether to generate a supposition object and whether to use
quantification.
