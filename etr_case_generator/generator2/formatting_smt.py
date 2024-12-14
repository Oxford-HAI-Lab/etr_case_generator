from pysmt.fnode import FNode
from etr_case_generator.ontology import Ontology


def format_smt(fnode: FNode) -> str:
    """Format SMT formula without single quotes around symbols and with proper quantifier symbols"""
    # First remove quotes
    formatted = str(fnode).replace("'", "")
    # Replace quantifier text with symbols
    formatted = formatted.replace("exists", "∃")
    formatted = formatted.replace("forall", "∀")
    return formatted


def smt_to_etr(fnode: FNode) -> str:
    """Convert an SMT formula to ETR notation.
    
    Rules:
    - If no quantifiers, wrap the whole expression in curly braces
    - If there are quantifiers, put curly braces after the quantifier: ∀x {f(x())}
    - No other curly braces should be used
    """
    def convert_inner(fnode: FNode) -> str:
        """Convert without adding outer braces"""
        # Base case: single predicate
        if fnode.is_symbol():
            expr = str(fnode).replace("'", "")
            if "(" in expr:  # If it's a predicate application
                name, arg = expr.split("(")
                arg = arg.rstrip(")")
                return f"{name}({arg}())"
            return expr

        # Handle each operator type
        if fnode.is_not():
            return f"~{convert_inner(fnode.arg(0))}"
        elif fnode.is_and():
            return "".join(convert_inner(arg) for arg in fnode.args())
        elif fnode.is_or():
            return ",".join(convert_inner(arg) for arg in fnode.args())
        elif fnode.is_implies():
            return f"{convert_inner(fnode.arg(0))}->{convert_inner(fnode.arg(1))}"
        elif fnode.is_iff():
            return f"{convert_inner(fnode.arg(0))}<->{convert_inner(fnode.arg(1))}"
        elif fnode.is_forall():
            vars = [str(v) for v in fnode.quantifier_vars()]
            return f"∀{','.join(vars)} {{{convert_inner(fnode.arg(0))}}}"
        elif fnode.is_exists():
            vars = [str(v) for v in fnode.quantifier_vars()]
            return f"∃{','.join(vars)} {{{convert_inner(fnode.arg(0))}}}"
        return str(fnode)  # Fallback

    # Only add outer braces if there are no quantifiers
    result = convert_inner(fnode)
    if not (fnode.is_exists() or fnode.is_forall()):
        result = "{" + result + "}"
    return result


def smt_to_english(fnode: FNode, ontology: Ontology) -> str:
    """Convert an SMT formula to natural English.

    Examples:
        magnetic(elementium) -> elementium is magnetic
        And(magnetic(x), radioactive(x)) -> x is magnetic and x is radioactive
        Or(magnetic(x), radioactive(x)) -> x is magnetic or x is radioactive
        Not(magnetic(x)) -> x is not magnetic
        Implies(magnetic(x), radioactive(x)) -> if x is magnetic then x is radioactive
        Iff(magnetic(x), radioactive(x)) -> x is magnetic if and only if x is radioactive
        ForAll([x], magnetic(x)) -> for all x, x is magnetic
        Exists([x], magnetic(x)) -> there exists an x such that x is magnetic
    """

    def _convert_predicate(pred_str: str) -> str:
        """Convert f(x) format to 'x is f'"""
        # Clean up the string first - remove any quotes
        pred_str = pred_str.replace("'", "")
        # Extract function name and argument from f(x) format
        name, arg = pred_str.split('(')
        arg = arg.rstrip(')')  # remove closing parenthesis
        # Replace underscores with spaces in predicate names
        name = name.replace('_', ' ')
        return f"{arg} is {name}"

    # Base case: single predicate
    if fnode.is_symbol():
        text = _convert_predicate(str(fnode))
        if text in ontology.natural_to_short_name_mapping:
            text = ontology.natural_to_short_name_mapping[text]
        return text

    # Handle each operator type
    if fnode.is_not():
        pred = smt_to_english(fnode.arg(0), ontology)
        # Replace "is" with "is not" for predicates
        return pred.replace(" is ", " is not ")

    elif fnode.is_and():
        terms = [smt_to_english(arg, ontology) for arg in fnode.args()]
        return " and ".join(terms)

    elif fnode.is_or():
        terms = [smt_to_english(arg, ontology) for arg in fnode.args()]
        return " or ".join(terms)

    elif fnode.is_implies():
        antecedent = smt_to_english(fnode.arg(0), ontology)
        consequent = smt_to_english(fnode.arg(1), ontology)
        return f"if {antecedent}, then {consequent}"

    elif fnode.is_iff():
        left = smt_to_english(fnode.arg(0), ontology)
        right = smt_to_english(fnode.arg(1), ontology)
        return f"{left} if and only if {right}"

    elif fnode.is_forall():
        vars = [str(v) for v in fnode.quantifier_vars()]
        body = smt_to_english(fnode.arg(0), ontology)
        return f"for all {', '.join(vars)}, {body}"

    elif fnode.is_exists():
        vars = [str(v) for v in fnode.quantifier_vars()]
        body = smt_to_english(fnode.arg(0), ontology)
        return f"there exists {', '.join(vars)} such that {body}"

    return str(fnode)  # Fallback for unknown operators
