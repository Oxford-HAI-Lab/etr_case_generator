# How to Create Problems

Use `generate_etr.py`. As of January 31, 2025, the other scripts in this directory are deprecated.

## Usage

This command was used to create the `datasets/fully_balanced_*.jsonl` files.

```bash
python scripts/generate_etr.py --save_file_name fully_balanced --question_type=all --generate_function=random_etr_problem -n 360 --balance_num_atoms --num_atoms_set 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 --balance
```

# Code Path

1. `generate_etr.py` is the main script that contains command line arguments
2. Its function `generate_problem_list` contains a for loop that builds up a list of problems. Within that is a while loop that iteratively throws out unacceptable or non-needed problems
3. It calls `generate_problem` in `generate_problem_from_logical.py`, which generates a bare-bones PartialProblem using the `generate_problem` function in `etr_generator_no_queue.py`
  * `generate_problem_from_logical.py` then converts that PartialProblem into a FullProblem by fleshing out the english form and such
4. `etr_generator_no_queue.py` generates problems randomly from a distribution. It builds up premises one at a time by creating random views. It requires the premises to have an interesting conclusion. This is the most interesting bit of logic.

