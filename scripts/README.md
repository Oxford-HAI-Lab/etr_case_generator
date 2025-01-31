# How to Create Problems

Use `generate_etr_2.py`. As of January 31, 2025, the other scripts in this directory are deprecated.

## Usage

This command was used to create the `datasets/fully_balanced_*.jsonl` files.

```bash
python scripts/generate_etr_2.py --save_file_name fully_balanced --question_type=all --generate_function=random_etr_problem -n 360 --balance_num_atoms --num_atoms_set 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 --balance
```