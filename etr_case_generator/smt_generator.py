from dataclasses import dataclass
from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Iff, is_valid
from pysmt.fnode import FNode
from pysmt.typing import BOOL, REAL, PySMTType


@dataclass(kw_only=True)
class SMTProblem:
    views: list[FNode] = None

    # Yes or No format
    yes_or_no_conclusion_correct: FNode = None
    yes_or_no_conclusion_incorrect: FNode = None  # Distractor
