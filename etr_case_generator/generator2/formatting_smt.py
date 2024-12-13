from pysmt.fnode import FNode


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

    Examples:
        magnetic(elementium) -> {magnetic(elementium)}  # wrapped in braces
        And(magnetic(x), radioactive(x)) -> {magnetic(x)radioactive(x)}  # remove 'and'
        Or(magnetic(x), radioactive(x)) -> {magnetic(x),radioactive(x)}  # use comma
        Not(magnetic(x)) -> {~magnetic(x)}  # use tilde
        Implies(magnetic(x), radioactive(x)) -> {magnetic(x)->radioactive(x)}  # use arrow
        Iff(magnetic(x), radioactive(x)) -> {magnetic(x)<->radioactive(x)}  # use double arrow
        ForAll([x], magnetic(x)) -> ∀x {magnetic(x)}  # quantifier with space
        Exists([x], magnetic(x)) -> ∃x {magnetic(x)}  # quantifier with space
    """
    def wrap_braces(expr: str) -> str:
        """Wrap expression in braces if not already quantified"""
        return "{" + expr + "}"
        # return expr

    # Base case: single predicate
    if fnode.is_symbol():
        # Remove quotes and add () after variable names
        expr = str(fnode).replace("'", "")
        if "(" in expr:  # If it's a predicate application
            name, arg = expr.split("(")
            arg = arg.rstrip(")")
            expr = f"{name}({arg}())"
        expr = wrap_braces(expr)
        return expr

    # Handle each operator type
    if fnode.is_not():
        return wrap_braces(f"~{smt_to_etr(fnode.arg(0)).strip('{}')}")

    elif fnode.is_and():
        return wrap_braces("".join(smt_to_etr(arg).strip('{}') for arg in fnode.args()))

    elif fnode.is_or():
        return wrap_braces(",".join(smt_to_etr(arg).strip('{}') for arg in fnode.args()))

    elif fnode.is_implies():
        return wrap_braces(f"{smt_to_etr(fnode.arg(0)).strip('{}')}->{smt_to_etr(fnode.arg(1)).strip('{}')}")

    elif fnode.is_iff():
        return wrap_braces(f"{smt_to_etr(fnode.arg(0)).strip('{}')}<->{smt_to_etr(fnode.arg(1)).strip('{}')}")

    elif fnode.is_forall():
        vars = [str(v) for v in fnode.quantifier_vars()]
        body = smt_to_etr(fnode.arg(0)).strip('{}')  # Remove existing braces from body
        return f"∀{','.join(vars)} {{{body}}}"  # Add new braces around body

    elif fnode.is_exists():
        vars = [str(v) for v in fnode.quantifier_vars()]
        body = smt_to_etr(fnode.arg(0)).strip('{}')  # Remove existing braces from body
        return f"∃{','.join(vars)} {{{body}}}"  # Add new braces around body

    return wrap_braces(str(fnode))  # Fallback for unknown operators


def smt_to_english(fnode: FNode) -> str:
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
        # Add () after the variable name
        return f"{arg}() is {name}"

    # Base case: single predicate
    if fnode.is_symbol():
        return _convert_predicate(str(fnode))

    # Handle each operator type
    if fnode.is_not():
        pred = smt_to_english(fnode.arg(0))
        # Replace "is" with "is not" for predicates
        return pred.replace(" is ", " is not ")

    elif fnode.is_and():
        terms = [smt_to_english(arg) for arg in fnode.args()]
        return " and ".join(terms)

    elif fnode.is_or():
        terms = [smt_to_english(arg) for arg in fnode.args()]
        return " or ".join(terms)

    elif fnode.is_implies():
        antecedent = smt_to_english(fnode.arg(0))
        consequent = smt_to_english(fnode.arg(1))
        return f"if {antecedent}, then {consequent}"

    elif fnode.is_iff():
        left = smt_to_english(fnode.arg(0))
        right = smt_to_english(fnode.arg(1))
        return f"{left} if and only if {right}"

    elif fnode.is_forall():
        vars = [str(v) for v in fnode.quantifier_vars()]
        body = smt_to_english(fnode.arg(0))
        return f"for all {', '.join(vars)}, {body}"

    elif fnode.is_exists():
        vars = [str(v) for v in fnode.quantifier_vars()]
        body = smt_to_english(fnode.arg(0))
        return f"there exists {', '.join(vars)} such that {body}"

    return str(fnode)  # Fallback for unknown operators
