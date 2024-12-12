from typing import List, Set, Tuple, Optional, Dict

from lm_eval.data_generation.random_logical.logical_literal import Literal

# Constants for compact form symbols
COMPACT_AND = ""  # Empty string represents AND in compact form
COMPACT_OR = ","
COMPACT_NOT = "~"
COMPACT_VARIABLE_WRAPPER = "()"

# Constants for standard form symbols
STANDARD_AND = " AND "
STANDARD_OR = " OR "
STANDARD_NOT = "NOT "

class LogicalStatement:
    """
    Represents a logical statement in Conjunctive Normal Form (CNF).

    A logical statement consists of a conjunction of clauses.
    """

    def __init__(self, clauses: List['Clause'], has_natural_language: bool = False):
        """
        Initialize a LogicalStatement with a list of clauses.

        Args:
            clauses (List[Clause]): A list of Clause objects.
            has_natural_language (bool): Whether natural language statements are available.
        """
        self.clauses: List[Clause] = clauses
        self.has_natural_language: bool = has_natural_language

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, and_symbol: Optional[str] = None, or_symbol: Optional[str] = None,
                  not_symbol: Optional[str] = None, use_natural_language: bool = False,
                  use_long_names: bool = False, use_compact_form: bool = False,
                  use_parentheses: bool = True) -> str:
        """
        Render the logical statement as a string with customizable symbols.

        Args:
            and_symbol (str): Symbol to use for conjunction. Defaults to STANDARD_AND.
            or_symbol (str): Symbol to use for disjunction. Defaults to STANDARD_OR.
            not_symbol (str): Symbol to use for negation. Defaults to STANDARD_NOT.
            use_natural_language (bool): Whether to use natural language if available. Defaults to False.
            use_long_names (bool): Whether to use long variable names. Defaults to False.
            use_compact_form (bool): Whether to use the compact form {A()B(),C()}. Defaults to False.
            use_parentheses (bool): Whether to enclose each clause in parentheses. Defaults to False.

        Returns:
            str: The rendered logical statement.

        Examples:
            >>> statement = LogicalStatement([Clause([Literal('A', 'Apple', False), Literal('B', 'Banana', True)])])
            >>> statement.to_string()
            '(Apple OR NOT Banana)'
            >>> statement.to_string(and_symbol='&', or_symbol='|', not_symbol='~')
            '(Apple | ~ Banana)'
            >>> statement.to_string(use_compact_form=True)
            '{A()~B()}'
            >>> statement.to_string(use_parentheses=True)
            '((Apple OR NOT Banana))'
            >>> statement.to_string(use_compact_form=True, use_parentheses=True)
            '({A()~B()})'
        """
        if use_compact_form:
            and_symbol = and_symbol or COMPACT_AND
            or_symbol = or_symbol or COMPACT_OR
            not_symbol = not_symbol or COMPACT_NOT
        else:
            and_symbol = and_symbol or STANDARD_AND
            or_symbol = or_symbol or STANDARD_OR
            not_symbol = not_symbol or STANDARD_NOT

        return self._to_standard_string(and_symbol, or_symbol, not_symbol, use_natural_language, use_long_names, use_parentheses)

    def _to_standard_string(self, and_symbol: str, or_symbol: str, not_symbol: str, 
                            use_natural_language: bool, use_long_names: bool, use_parentheses: bool) -> str:
        """
        Render the logical statement in standard form.

        Args:
            and_symbol (str): Symbol to use for conjunction.
            or_symbol (str): Symbol to use for disjunction.
            not_symbol (str): Symbol to use for negation.
            use_natural_language (bool): Whether to use natural language if available.
            use_long_names (bool): Whether to use long variable names.
            use_parentheses (bool): Whether to enclose each clause in parentheses.

        Returns:
            str: The rendered logical statement in standard form.

        Examples:
            >>> statement = LogicalStatement([
            ...     Clause([Literal('A', 'Apple', False, ('Apple is red', 'Apple is not red')), 
            ...             Literal('B', 'Banana', True, ('Banana is yellow', 'Banana is not yellow'))])
            ... ])
            >>> statement._to_standard_string('AND', 'OR', 'NOT', False, False, False)
            'A OR NOT B'
            >>> statement._to_standard_string('&', '|', '~', True, True, True)
            '(Apple is red | Banana is not yellow)'
        """
        clause_strings = []
        for clause in self.clauses:
            literal_strings = []
            for literal in clause.literals:
                if literal.statements and self.has_natural_language and use_natural_language:
                    literal_str = literal.statements[1] if literal.negated else literal.statements[0]
                else:
                    variable_name = literal.variable_name if use_long_names else literal.variable_short
                    variable_name = variable_name.strip()
                    literal_str = f"{not_symbol}{variable_name}()" if literal.negated else f"{variable_name}()"
                literal_strings.append(literal_str)
            clause_str = f"{or_symbol}".join(literal_strings)
            if use_parentheses:
                clause_str = f"({clause_str})"
            clause_strings.append(clause_str)
        return f"{and_symbol}".join(clause_strings)

    def add_clause(self, clause: 'Clause') -> None:
        self.clauses.append(clause)

    @property
    def variables(self) -> List[str]:
        all_vars: Set[str] = set()
        for clause in self.clauses:
            all_vars.update(literal.variable_short for literal in clause.literals)
        return sorted(list(all_vars))

    def find_satisfying(self) -> List[Dict[str, bool]]:
        """
        Find all satisfying assignments for the logical statement.

        Returns:
            List[Dict[str, bool]]: A list of dictionaries, where each dictionary
            represents a satisfying assignment of variables.
        """
        variables = self.variables
        satisfying_assignments = []

        for assignment in self._generate_assignments(variables):
            if self._evaluate(assignment):
                satisfying_assignments.append(assignment)

        return satisfying_assignments

    def _generate_assignments(self, variables: List[str]) -> List[Dict[str, bool]]:
        """
        Generate all possible assignments for the given variables.

        Args:
            variables (List[str]): List of variable names.

        Returns:
            List[Dict[str, bool]]: List of all possible variable assignments.
        """
        if not variables:
            return [{}]

        variable = variables[0]
        sub_assignments = self._generate_assignments(variables[1:])
        assignments = []

        for sub_assignment in sub_assignments:
            true_assignment = sub_assignment.copy()
            true_assignment[variable] = True
            assignments.append(true_assignment)

            false_assignment = sub_assignment.copy()
            false_assignment[variable] = False
            assignments.append(false_assignment)

        return assignments

    def _evaluate(self, assignment: Dict[str, bool]) -> bool:
        """
        Evaluate the logical statement for a given assignment.

        Args:
            assignment (Dict[str, bool]): A dictionary mapping variables to boolean values.

        Returns:
            bool: True if the assignment satisfies the logical statement, False otherwise.
        """
        return all(clause._evaluate(assignment) for clause in self.clauses)

    def find_necessary_assignments(self) -> Dict[str, Optional[bool]]:
        """
        Find variables that must be true or false in all satisfying assignments.

        Returns:
            Dict[str, Optional[bool]]: A dictionary mapping variables to their necessary assignments.
                                       True means the variable must be true, False means it must be false,
                                       and None means the variable can be either true or false.
        """
        satisfying_assignments = self.find_satisfying()
        
        if not satisfying_assignments:
            return {}  # No satisfying assignments, so no necessary assignments

        necessary_assignments = {}
        variables = self.variables

        for var in variables:
            all_true = all(assignment[var] for assignment in satisfying_assignments)
            all_false = all(not assignment[var] for assignment in satisfying_assignments)

            if all_true:
                necessary_assignments[var] = True
            elif all_false:
                necessary_assignments[var] = False
            else:
                necessary_assignments[var] = None

        return necessary_assignments

    def find_follows(self) -> 'LogicalStatement':
        """
        Find all statements that necessarily follow from this logical statement.

        Returns:
            LogicalStatement: A new LogicalStatement containing all necessary conclusions.
        """
        necessary_assignments = self.find_necessary_assignments()
        
        # Create literals for each necessary assignment
        follow_literals = []
        for var, value in necessary_assignments.items():
            if value is not None:  # Only include definite assignments
                # Find the original Literal object for this variable
                original_literal = next(
                    literal for clause in self.clauses 
                    for literal in clause.literals 
                    if literal.variable_short == var
                )
                
                # Create a new Literal with the necessary assignment
                new_literal = Literal(
                    variable_short=var,
                    variable_name=original_literal.variable_name,
                    negated=not value,  # Negate if the necessary value is False
                    statements=original_literal.statements
                )
                follow_literals.append(new_literal)
        
        # If there are no necessary conclusions, return a LogicalStatement that's always true
        if not follow_literals:
            return LogicalStatement([Clause([Literal("T", "True", negated=False, statements=("True", "False"))])])
        
        # Create a new Clause with all the follow literals
        follow_clause = Clause(follow_literals)
        
        # Create and return a new LogicalStatement with this single clause
        return LogicalStatement([follow_clause], has_natural_language=self.has_natural_language)

    def to_proposition_list(self) -> str:
        """
        Convert the logical statement to a list of propositions.

        Returns:
            str: A string representation of the logical statement as a list of propositions.
        """
        propositions = []

        # Process main clauses
        for i, clause in enumerate(self.clauses, 1):
            proposition = f"P{i} {clause.to_string(or_symbol=', OR ', use_natural_language=self.has_natural_language, use_long_names=True)}."
            propositions.append(proposition)

        # Process follows clauses
        follows = self.find_follows()
        for i, clause in enumerate(follows.clauses, 1):
            prefix = "C  " if len(follows.clauses) == 1 else f"C{i} "
            proposition = f"{prefix}{clause.to_string(or_symbol=', or ', use_natural_language=self.has_natural_language, use_long_names=True)}."
            propositions.append(proposition)
        
        return "\n".join(propositions)

class Clause:
    """
    Represents a clause in a logical statement.

    A clause is a disjunction of literals.
    """

    def __init__(self, literals: List['Literal']):
        """
        Initialize a Clause with a list of literals.

        Args:
            literals (List[Literal]): A list of Literal objects.
        """
        self.literals: List[Literal] = literals

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, or_symbol: str = STANDARD_OR, not_symbol: str = STANDARD_NOT,
                  use_natural_language: bool = False, use_long_names: bool = False) -> str:
        """
        Render the clause as a string with customizable symbols.

        Args:
            or_symbol (str): Symbol to use for disjunction. Defaults to STANDARD_OR.
            not_symbol (str): Symbol to use for negation. Defaults to STANDARD_NOT.
            use_natural_language (bool): Whether to use natural language if available. Defaults to False.
            use_long_names (bool): Whether to use long variable names. Defaults to False.

        Returns:
            str: The rendered clause.
        """
        literal_strings = []
        for literal in self.literals:
            if literal.statements and use_natural_language:
                literal_str = literal.statements[1] if literal.negated else literal.statements[0]
            else:
                variable_name = literal.variable_name if use_long_names else literal.variable_short
                literal_str = f"{not_symbol} {variable_name}" if literal.negated else variable_name
            literal_strings.append(literal_str.strip())
        return f" {or_symbol} ".join(literal_strings)

    def to_compact_string(self, or_symbol: str = COMPACT_OR, use_long_names: bool = False) -> str:
        """
        Render the clause in compact form.

        Args:
            or_symbol (str): Symbol to use for disjunction in compact form. Defaults to COMPACT_OR.
            use_long_names (bool): Whether to use long variable names. Defaults to False.

        Returns:
            str: The rendered clause in compact form.
        """
        literal_strings = []
        for literal in self.literals:
            variable_name = literal.variable_name if use_long_names else literal.variable_short
            literal_str = f"{COMPACT_NOT}{variable_name}{COMPACT_VARIABLE_WRAPPER}" if literal.negated else f"{variable_name}{COMPACT_VARIABLE_WRAPPER}"
            literal_strings.append(literal_str)
        return f"{or_symbol}".join(literal_strings)

    def add_literal(self, literal: 'Literal') -> None:
        self.literals.append(literal)

    def _evaluate(self, assignment: Dict[str, bool]) -> bool:
        """
        Evaluate the clause for a given assignment.

        Args:
            assignment (Dict[str, bool]): A dictionary mapping variables to boolean values.

        Returns:
            bool: True if the assignment satisfies the clause, False otherwise.
        """
        return any(literal._evaluate(assignment) for literal in self.literals)
