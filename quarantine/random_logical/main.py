from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from lm_eval.data_generation.random_logical.generate_random_questions import generate_random_cnf
from lm_eval.data_generation.random_logical.generate_random_questions import generate_random_cnf
from lm_eval.data_generation.random_logical.logical_question import LogicalQuestion
from lm_eval.data_generation.random_logical.logical_statement import LogicalStatement


def main() -> None:
    console = Console()

    cnf1: LogicalStatement = generate_random_cnf(num_clauses=3, max_literals_per_clause=2, num_variables=4)
    console.print(Panel(
        "Default rendering:\n" +
        str(cnf1) +
        "\n\nCustom rendering with '&' and '~':\n" +
        cnf1.to_string(and_symbol="&", not_symbol="~") +
        f"\n\nVariables used: {', '.join(cnf1.variables)}",
        title="Example 1: Small CNF (3 clauses, max 2 literals per clause, 4 variables)",
        style="bold magenta"
    ))
    
    cnf2: LogicalStatement = generate_random_cnf(num_clauses=5, max_literals_per_clause=3, num_variables=6)
    console.print(Panel(
        "Default rendering:\n" +
        str(cnf2) +
        "\n\nCustom rendering with '∧' and '¬':\n" +
        cnf2.to_string(and_symbol="∧", not_symbol="¬") +
        f"\n\nVariables used: {', '.join(cnf2.variables)}",
        title="Example 2: Medium CNF (5 clauses, max 3 literals per clause, 6 variables)",
        style="bold magenta"
    ))
    
    cnf3: LogicalStatement = generate_random_cnf(num_clauses=8, max_literals_per_clause=4, num_variables=8)
    console.print(Panel(
        "Default rendering:\n" +
        str(cnf3) +
        "\n\nCustom rendering with 'AND' and 'NOT':\n" +
        cnf3.to_string(and_symbol="AND", not_symbol="NOT") +
        f"\n\nVariables used: {', '.join(cnf3.variables)}",
        title="Example 3: Large CNF (8 clauses, max 4 literals per clause, 8 variables)",
        style="bold magenta"
    ))

    cnf4: LogicalStatement = generate_random_cnf(num_clauses=5, max_literals_per_clause=3, num_variables=6, use_natural_language=True)
    console.print(Panel(
        "Default rendering:\n" +
        str(cnf4) +
        "\n\nCustom rendering with '&&' and '!':\n" +
        cnf4.to_string(and_symbol="&&", not_symbol="!") +
        f"\n\nVariables used: {', '.join(cnf4.variables)}",
        title="Example 4: Natural Language CNF (5 clauses, max 3 literals per clause, 6 variables)",
        style="bold magenta"
    ))

    cnf5: LogicalStatement = generate_random_cnf(num_clauses=3, max_literals_per_clause=2, num_variables=3, use_natural_language=True)
    console.print(Panel(
        "Most compact rendering (variables only):\n" +
        cnf5.to_string(and_symbol="&", not_symbol="~", use_natural_language=False) +
        "\n\nMost verbose rendering (variables only):\n" +
        cnf5.to_string(and_symbol=" AND ", not_symbol="NOT ", use_natural_language=False) +
        "\n\nNatural language rendering:\n" +
        cnf5.to_string(and_symbol=" AND ", not_symbol="NOT ", use_natural_language=True) +
        "\n\nCompact form rendering:\n" +
        cnf5.to_string(),
        title="Example 5: Small CNF with compact, verbose, natural language, and compact form rendering",
        style="bold magenta"
    ))

    cnf6: LogicalStatement = generate_random_cnf(num_clauses=3, max_literals_per_clause=2, num_variables=3, use_natural_language=False)
    satisfying_assignments = cnf6.find_satisfying()
    console.print(Panel(
        "Logical statement:\n" +
        str(cnf6) +
        "\n\nSatisfying assignments:\n" +
        ("\n".join(str(assignment) for assignment in satisfying_assignments) if satisfying_assignments else "No satisfying assignments found."),
        title="Example 6: Finding satisfying assignments",
        style="bold magenta"
    ))

    cnf7: LogicalStatement = generate_random_cnf(num_clauses=4, max_literals_per_clause=2, num_variables=4, use_natural_language=False)
    necessary_assignments = cnf7.find_necessary_assignments()
    console.print(Panel(
        "Logical statement:\n" +
        str(cnf7) +
        "\n\nNecessary assignments:\n" +
        "\n".join(f"{var} must be {'True' if value is True else 'False' if value is False else 'either True or False'}" for var, value in necessary_assignments.items()),
        title="Example 7: Finding necessary assignments",
        style="bold magenta"
    ))

    console.print(Panel("Generating Logical Questions", title="Example 8", style="bold magenta"))
    from lm_eval.data_generation.random_logical.generate_random_questions import create_random_questions
    questions: list[LogicalQuestion] = create_random_questions(n=3, num_clauses=4, max_literals_per_clause=3, num_variables=5, use_natural_language=True)
    for i, question in enumerate(questions, 1):
        console.print(Panel(question.string_representation + f"\n\nNum Clauses:{question.num_clauses}\nNum Variables: {question.num_variables}\nNum Follows: {len(question.get_follows())}", title=f"Question {i}: Statement", style="bold cyan"))
        console.print(Panel(
            "\n".join(f"{var} must be {'True' if value is True else 'False' if value is False else 'either True or False'}" for var, value in question.necessary_assignments.items()),
            title=f"Question {i}: Necessary Assignments",
            style="bold green"
        ))
        console.print(Panel(
            "\n".join(f"- {follow}" for follow in question.get_follows()),
            title=f"Question {i}: Follows (each of these follow)",
            style="bold yellow"
        ))
        print()  # Add an empty line between questions for better readability

if __name__ == "__main__":
    main()
