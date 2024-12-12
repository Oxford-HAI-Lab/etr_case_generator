import os
from datetime import datetime
from lm_eval.data_generation.random_logical.logical_question import LogicalQuestion
from lm_eval.data_generation.random_logical.generate_random_questions import create_random_questions
from lm_eval.data_generation.random_logical.logical_statement import LogicalStatement, COMPACT_AND, COMPACT_OR


def generate_case_file(questions: list[LogicalQuestion], file_name: str) -> None:
    """
    Generate a new Python file with case classes based on the given LogicalQuestions.

    Args:
    questions (list[LogicalQuestion]): List of LogicalQuestion objects to convert into case classes.
    file_name (str): Name of the file to create (without .py extension).
    """
    output_dir = 'lm_eval/data_generation/random_logical/generated'
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, f"{file_name}.py")

    with open(file_path, 'w') as f:
        f.write(f"# Generated code - DO NOT EDIT\n")
        f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("from pyetr import View\n")
        f.write("from pyetr.cases import BaseExample, ps\n")
        f.write("from typing import List\n\n")

        for i, question in enumerate(questions, 1):
            class_name = f"GeneratedCase{i}"
            f.write(f"class {class_name}(BaseExample):\n")
            prop_list = question.statement.to_proposition_list()
            prop_list = prop_list.replace("\n", "\n    ")
            docstring = f'    """\n    Example {i}\n\n    {prop_list}\n    """\n\n'
            f.write(docstring)
            
            # Generate the 'v' variable
            statement: LogicalStatement = question.statement
            statement_str = statement.to_string(use_compact_form=True, use_long_names=False, or_symbol=" ∨ ", and_symbol=" ∧ ", use_parentheses=True)
            f.write(f"    v: tuple[View, ...] = (ps(\"{statement_str}\"),)\n")
            
            # Generate the 'c' variable
            necessary_assignments = question.statement.find_necessary_assignments()
            c_parts = []
            for var, value in necessary_assignments.items():
                if value is True:
                    c_parts.append(f"{var}()")
                elif value is False:
                    c_parts.append(f"~{var}()")
            c_str = ",".join(c_parts)
            f.write(f"    c: View = ps(\"{{{c_str}}}\")\n")

            # Add more information about the LogicalStatement
            f.write(f"    full_text: str = \"{question.string_representation}\"\n")
            f.write(f"    follows: List[str] = {question.get_follows()}\n\n")
            f.write(f"    # Difficulty information\n")
            f.write(f"    num_clauses: int = {question.num_clauses}\n")
            f.write(f"    num_variables: int = {question.num_variables}\n")
            f.write(f"    variables: List[str] = {question.statement.variables}\n")
            f.write(f"    num_follows: int = {len(question.get_follows())}\n\n\n")

    print(f"Created file: {file_path}")

def main():
    num_each = 10

    # Generate easy questions
    easy_questions = create_random_questions(n=num_each, num_clauses=2, min_literals_per_clause=2, max_literals_per_clause=2, num_variables=3, use_natural_language=True, num_follows=1)
    generate_case_file(easy_questions, "generated_cases_easy")

    # Generate medium questions
    medium_questions = create_random_questions(n=num_each, num_clauses=3, min_literals_per_clause=2, max_literals_per_clause=3, num_variables=4, use_natural_language=True, num_follows=1)
    generate_case_file(medium_questions, "generated_cases_medium")

    # Generate hard questions
    hard_questions = create_random_questions(n=num_each, num_clauses=4, min_literals_per_clause=2, max_literals_per_clause=5, num_variables=5, use_natural_language=True, num_follows=1)
    generate_case_file(hard_questions, "generated_cases_hard")

    # Generate super hard questions
    super_hard_questions = create_random_questions(n=num_each, num_clauses=5, min_literals_per_clause=2, max_literals_per_clause=6, num_variables=8, use_natural_language=True, num_follows=1)
    generate_case_file(super_hard_questions, "generated_cases_super_hard")

if __name__ == "__main__":
    main()
