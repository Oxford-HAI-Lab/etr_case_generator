# etr_case_generator

This is a tool for generating problems to evaluate the erotetic theory of reasoning. 

## Setup

```bash
pip install -r requirements.txt
```

Possibly necessary for some scripting:
```bash
export PYTHONPATH=/path/to/your/etr_case_generator/etr_case_generator:$PYTHONPATH
```

## Generation

Run this command:

```bash
python scripts/generate_etr_for_lm_eval.py -n 10
```

This will generate 10 problems and save them to a file called `datasets/etr_for_lm_eval.jsonl`. It's important that it be in this location, so that lm_eval can find it. 

See the [lm_eval documentation](lm_eval/tasks/README.md) for more information on how to use this dataset with lm_eval.

## Inspecting the Dataset

You can use the `pprint_problems` script to inspect the dataset. 

```bash
pip install pprint_problems
```

Then, here are some ways you can inspect it.

Show the details of 10 random problems:

```bash
pprint_problems datasets/etr_for_lm_eval.jsonl -n 10 -r
```

Show the structure of the dataset:

```bash
pprint_problems datasets/etr_for_lm_eval.jsonl --structure
```

Look at just the question, premises, and conclusion for 3 random problems:

```bash
pprint_problems datasets/etr_for_lm_eval.jsonl -n 3 -r --parts question scoring_guide/premises scoring_guide/question_conclusion
```

Show stats about the dataset:

```bash
pprint_problems datasets/etr_for_lm_eval.jsonl -p scoring_guide/etr_answer scoring_guide/logically_correct_answer --stats --full_combinatoric
```
