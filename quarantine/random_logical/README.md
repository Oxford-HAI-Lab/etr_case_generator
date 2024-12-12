# Random Logical Statement Generator

This directory contains scripts for generating random logical statements and questions based on those statements.

## Running the Scripts

### main.py

This script generates and displays various examples of random logical statements.

To run:
```
python main.py
```

This script doesn't take any command-line arguments. It demonstrates different ways of generating and rendering logical statements.

### questions_to_cases.py

This script generates Python case classes based on randomly generated logical questions.

To run:
```
python questions_to_cases.py
```

This script generates three sets of questions (easy, medium, and hard) and creates corresponding Python files with case classes.

#### Customization

You can modify the following parameters in the `main()` function of `questions_to_cases.py`:

- `num_each`: Number of questions to generate for each difficulty level
- Easy questions: `num_clauses=2, max_literals_per_clause=2, num_variables=3`
- Medium questions: `num_clauses=3, max_literals_per_clause=3, num_variables=4`
- Hard questions: `num_clauses=4, max_literals_per_clause=3, num_variables=5`

Adjust these parameters to generate questions of different complexity.

## Usage

These scripts can be used to:
1. Generate random logical statements for testing or educational purposes
2. Create sets of logical questions with varying difficulty levels
3. Automatically generate Python case classes for use in larger projects or test suites

Feel free to modify the scripts to suit your specific needs or integrate them into larger projects.
