# Using `lm_eval` with the ETR Case Generator

## Generate Problems

Run this command to generate problems:

```bash
python scripts/generate_etr_for_lm_eval.py
```

This will generate problems in the `datasets/` directory. Unless you have a good reason, keep the default of `datasets/etr_for_lm_eval.jsonl`, whose file name is referenced by `etr_problems.yaml`. 

## Evaluate Problems

First, ensure that you have the `lm-evaluation-harness` repository cloned and installed from [here](https://github.com/EleutherAI/lm-evaluation-harness). You can run `git clone https://github.com/EleutherAI/lm-evaluation-harness.git`.

Then, run this command to evaluate the generated problems:

```bash
lm_eval/tasks/etr_problems/run_evaluation.sh
```

Or, this fuller command, in which you will need to specify the full paths to the `lm-evaluation-harness` and `etr_case_generator` repositories, and the model you want to evaluate with:

```bash
lm_eval/tasks/etr_problems/run_evaluation.sh -p /path/to/lm-evaluation-harness -i /path/to/etr_case_generator  -m gpt-4-turbo
```

Running this command will print out the results of the evaluation. You can see the full results of the run in `lm_eval/tasks/etr_problems/results/`. In particular, the `samples` jsonl file there will contain "resps" objects which are the model's responses to the problems.

## Viewing Results

After running the evaluation, the results will be stored in `lm_eval/tasks/etr_problems/results/`. You can view the results in a more human-readable format with this util:

```bash
pip install pprint_problems
```

Then, run this command to view the results:

```bash
pprint_problems lm_eval/tasks/etr_problems/results/MODEL_NAME_HERE/SAMPLES_FILE.json -p doc/question resps correct doc/scoring_guide/etr_conclusion doc/scoring_guide/etr_conclusion_is_categorical -n 3 -r
```

This will print out the questions, the model's responses, the correct answers, and the scoring guide for the ETR conclusion. You can adjust the `-n` flag to print out more or fewer results. The `-r` flag will randomize the order of the results.