import random
from typing import List, Tuple, Optional

from lm_eval.data_generation.random_logical.logical_statement import LogicalStatement, Literal, Clause
from lm_eval.data_generation.random_logical.logical_question import LogicalQuestion
from lm_eval.data_generation.random_logical.variable_loader import load_variable_statements, get_all_themes


def generate_literal(variables: List[dict]) -> Literal:
    random_var = random.choice(variables)
    variable_short, variable_name, positive, negative = random_var['variable_short'], random_var['variable_name'], \
    random_var['positive'], random_var['negative']
    negated: bool = random.choice([True, False])
    return Literal(variable_short, variable_name.capitalize(), negated, (positive, negative))


def generate_literal_from_dict(variable: dict) -> Literal:
    variable_short, variable_name, positive, negative = variable['variable_short'], variable['variable_name'], variable[
        'positive'], variable['negative']
    negated: bool = random.choice([True, False])
    return Literal(variable_short, variable_name.capitalize(), negated, (positive, negative))


def generate_clause(variables: List[dict], min_literals_per_clause: int, max_literals_per_clause: int) -> Clause:
    assert min_literals_per_clause <= max_literals_per_clause, "min_literals_per_clause must be <= max_literals_per_clause"
    assert max_literals_per_clause <= len(variables), "max_literals_per_clause must be <= num_variables"

    max_attempts = len(variables) * 100  # Limit the number of attempts to avoid infinite loops
    for attempt in range(max_attempts):
        num_literals: int = random.randint(min_literals_per_clause, max_literals_per_clause)
        literals: List[Literal] = []
        used_variables = set()

        for _ in range(num_literals):
            available_variables = [var for var in variables if var["variable_short"] not in used_variables]
            if not available_variables:
                break
            variable = random.choice(available_variables)
            literal = generate_literal_from_dict(variable)
            literals.append(literal)
            used_variables.add(literal.variable_short)

        if len(literals) >= min_literals_per_clause:
            return Clause(literals)
        # else:
        #     print(f"Not enough literals in clause, retrying... {[literal.variable_short for literal in literals]} out of {[var[0] for var in variables]}")

    raise ValueError(
        f"Failed to generate a valid clause after {max_attempts} attempts, with min_literals_per_clause={min_literals_per_clause}, max_literals_per_clause={max_literals_per_clause}, and num_variables={len(variables)}")


def _generate_random_cnf(num_clauses: int, min_literals_per_clause: int, max_literals_per_clause: int,
                         num_variables: int, use_natural_language: bool = False) -> LogicalStatement:
    variable_statements = load_variable_statements('lm_eval/data_generation/random_logical/variable_statements.json')
    themes = get_all_themes(variable_statements)
    chosen_theme = random.choice(themes)
    theme_variables = variable_statements[chosen_theme]
    if len(theme_variables) < num_variables:
        raise ValueError(
            f"Not enough unique variables in the chosen theme. Required: {num_variables}, Available: {len(theme_variables)}")
    variables: List[dict] = random.sample(theme_variables, num_variables)

    clauses: List[Clause] = [generate_clause(variables, min_literals_per_clause, max_literals_per_clause) for _ in
                             range(num_clauses)]
    return LogicalStatement(clauses, has_natural_language=True)


def _generate_random_question(num_clauses: int, min_literals_per_clause: int, max_literals_per_clause: int,
                              num_variables: int, use_natural_language: bool = False,
                              num_follows: int = 1) -> LogicalQuestion:
    variable_statements = load_variable_statements('lm_eval/data_generation/random_logical/variable_statements.json')
    themes = get_all_themes(variable_statements)
    chosen_theme = random.choice(themes)
    theme_variables = variable_statements[chosen_theme]
    if len(theme_variables) < num_variables:
        raise ValueError(
            f"Not enough unique variables in the chosen theme. Required: {num_variables}, Available: {len(theme_variables)}")
    variables: List[dict] = random.sample(theme_variables, num_variables)

    clauses: List[Clause] = []
    statement = LogicalStatement(clauses, has_natural_language=use_natural_language)

    max_attempts = num_clauses * 10  # Limit the number of attempts to avoid infinite loops
    for _ in range(max_attempts):
        if len(clauses) >= num_clauses:
            break

        new_clause = generate_clause(variables, min_literals_per_clause, max_literals_per_clause)
        clauses.append(new_clause)
        statement = LogicalStatement(clauses, has_natural_language=use_natural_language)

        question = LogicalQuestion(statement)

        follows_count = len(question.get_follows())

        if follows_count < num_follows:
            clauses.pop()  # Remove the last clause if it reduces the number of follows too much
        elif follows_count == num_follows:
            return question  # We've found a question with the desired number of follows

    # If we couldn't generate a question with the exact number of follows, return the best we have
    return LogicalQuestion(statement)


def create_random_questions(n: int, num_clauses: int, min_literals_per_clause: int, max_literals_per_clause: int,
                            num_variables: int, use_natural_language: bool = False,
                            num_follows: Optional[int] = None) -> List[LogicalQuestion]:
    questions = []
    attempts = 0
    max_attempts = n * 100  # Cap overgeneration

    while len(questions) < n and attempts < max_attempts:
        question = _generate_random_question(num_clauses, min_literals_per_clause, max_literals_per_clause,
                                             num_variables, use_natural_language, num_follows)
        # print(f"Generated question: {question}")
        # questions.append(question)
        statement = _generate_random_cnf(num_clauses, min_literals_per_clause, max_literals_per_clause, num_variables,
                                         use_natural_language)
        necessary_assignments = statement.find_necessary_assignments()

        if any(value is not None for value in necessary_assignments.values()):
            string_representation = statement.to_string(use_natural_language=use_natural_language)
            question = LogicalQuestion(statement)

            if num_follows is None or len(question.get_follows()) == num_follows:
                questions.append(question)

        attempts += 1

    return questions
