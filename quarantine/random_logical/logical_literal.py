from typing import Optional, Tuple, Dict


class Literal:
    """
    Represents a literal in a logical statement.

    A literal is either a variable or its negation.
    """

    def __init__(self, variable_short: str, variable_name: str, negated: bool = False, statements: Optional[Tuple[str, str]] = None):
        """
        Initialize a Literal with a variable, its negation status, and optional statements.

        Args:
            variable_short (str): The short variable name.
            variable_name (str): The full variable name.
            negated (bool, optional): Whether the literal is negated. Defaults to False.
            statements (Optional[Tuple[str, str]]): Positive and negative statements for the variable.
        """
        self.variable_short: str = variable_short
        self.variable_name: str = variable_name
        self.negated: bool = negated
        self.statements: Optional[Tuple[str, str]] = statements

    def __str__(self) -> str:
        if self.statements:
            return self.statements[1] if self.negated else self.statements[0]
        return f"NOT {self.variable_short}" if self.negated else self.variable_short

    def _evaluate(self, assignment: Dict[str, bool]) -> bool:
        """
        Evaluate the literal for a given assignment.

        Args:
            assignment (Dict[str, bool]): A dictionary mapping variables to boolean values.

        Returns:
            bool: True if the assignment satisfies the literal, False otherwise.
        """
        value = assignment[self.variable_short]
        return not value if self.negated else value