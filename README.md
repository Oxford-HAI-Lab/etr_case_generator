# etr_case_generator

Welcome! `etr_case_generator` is a generation tool for producing datasets of reasoning problems. These problems are constructed to test the [Erotetic Theory of Reasoning](https://academic.oup.com/book/45443), though they can be used to assess general soundness in predicate reasoning, and are largely tailored for prompting LLMs.

This system utilises ETR's predicate calculus with the [`PyETR`](https://github.com/Oxford-HAI-Lab/PyETR) package. For now, we do not use the extensions for probabilistic reasoning and decision-making.

## Setup

`etr_case_generator` works with Python 3.12.5 and may work with other versions. Here, mileage may vary, but one might do this with:

```bash
python3.12 -m venv .env
source .env/bin/activate
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

2. **LM-Eval Environment for Running Evaluations**
   The generated cases can be evaluated using lm-eval, which is installed separately using pipx.
   Install dependencies in the lm-eval environment:
   ```bash
   # Install PyETR in lm-eval's environment
   ~/.local/pipx/venvs/lm-eval/bin/python -m pip install -e ~/Dev/PyETR_fork/
   
   # Install other required dependencies
   ~/.local/pipx/venvs/lm-eval/bin/python -m pip install pysmt rich openai dataclasses_json
   
   # Install this package
   ~/.local/pipx/venvs/lm-eval/bin/python -m pip install -e ~/Dev/etr_case_generator/
   ```

## Generation

## Generating Individual Views

The `etr_case_generator.generator` module exposes a class called `ETRCaseGenerator`,
which is designed for generating either individual `pyetr.View` objects or entire
reasoning problems.

`ETRCaseGenerator.generate_view` returns a single random view with some configurable
number of disjunctions, conjuncts, and a configurable rate of randomly negated atoms. In
addition, you can specify whether to generate a supposition object and whether to use
quantification.

## Generating Whole Reasoning Problems

Run this command:

```bash
python scripts/generate_etr_2.py --save_file_name dev --question_type=all --generate_function=random_etr_problem -n 10
```

This will generate 10 problems and save them to 3 files called `datasets/dev_yes_no.jsonl` and similar.  

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
