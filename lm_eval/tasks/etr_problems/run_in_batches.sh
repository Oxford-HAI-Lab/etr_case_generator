

# TODO Take a file like /home/keenan/Dev/etr_case_generator/datasets/balance_atoms_open_ended.jsonl
# TODO Shuffle that file line by line
# TODO Split that file up into n=20 evenly sized files, line by line

# TODO For each of those files, run a command like this:
# lm_eval/tasks/etr_problems/run_evaluation.sh --dataset partial_dataset.jsonl -m deepseek-r1

# TODO The run_evaluation.sh script might crash, and in that case, try to run it again