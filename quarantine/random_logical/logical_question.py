from typing import List
from lm_eval.data_generation.random_logical.logical_statement import LogicalStatement

class LogicalQuestion:
    def __init__(self, statement: LogicalStatement):
        self.statement: LogicalStatement = statement

    def __str__(self) -> str:
        return f"Question: {self.statement.to_string(use_natural_language=True)}\nNecessary assignments: {self.statement.find_necessary_assignments()}"

    def get_follows(self) -> List[str]:
        follows = []
        necessary_assignments = self.statement.find_necessary_assignments()
        for var, value in necessary_assignments.items():
            literal = next(literal for clause in self.statement.clauses for literal in clause.literals if literal.variable_short == var)
            if value is True:
                follows.append(literal.statements[0])
            elif value is False:
                follows.append(literal.statements[1])
        return follows

    def generate_full_text(self) -> str:
        propositions = self.statement.to_proposition_list()
        conclusion = self.generate_conclusion()
        return f"{propositions}\n\n{conclusion}"

    def generate_conclusion(self) -> str:
        follows = self.get_follows()
        if follows:
            return "C " + " and ".join(follows) + "."
        else:
            return "C No definite conclusion can be drawn."

    @property
    def num_clauses(self) -> int:
        return len(self.statement.clauses)

    @property
    def num_variables(self) -> int:
        return len(self.statement.variables)

    @property
    def string_representation(self) -> str:
        return self.statement.to_string(use_natural_language=True)
