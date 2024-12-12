# File 3: CVC5 Examples (Python API)

import cvc5


def example_1():
    print("\nExample 1: Quantified View in CVC5")
    pyetr_formula = "∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}"
    print("Inspired PyETR Formula:", pyetr_formula)

    solver = cvc5.Solver()
    solver.setOption("produce-models", "true")
    solver.setLogic("ALL")

    bool_sort = solver.getBooleanSort()

    Student = solver.mkConst(bool_sort, "Student")
    Reads = solver.mkConst(bool_sort, "Reads")
    Book = solver.mkConst(bool_sort, "Book")
    z = solver.mkVar(bool_sort, "z")
    w = solver.mkVar(bool_sort, "w")

    # Create the inner term first
    inner_term = solver.mkTerm(cvc5.Kind.EQUAL, Reads, Book)
    
    # Create a bound variable list for exists
    bound_vars_exists = solver.mkTerm(cvc5.Kind.VARIABLE_LIST, w)
    exists_w = solver.mkTerm(cvc5.Kind.EXISTS, bound_vars_exists, inner_term)
    
    # Create a bound variable list for forall
    bound_vars_forall = solver.mkTerm(cvc5.Kind.VARIABLE_LIST, z)
    forall_z = solver.mkTerm(cvc5.Kind.FORALL, bound_vars_forall, exists_w)
    solver.assertFormula(forall_z)

    print("Expression (CVC5 representation):", str(forall_z))
    print("Expression (string representation):", str(forall_z))

    result = solver.checkSat()
    if result.isSat():
        print("Satisfiable. Model:")
        print(solver.getValue(Student))
        print(solver.getValue(Reads))
        print(solver.getValue(Book))
    else:
        print("Unsatisfiable")


def example_2():
    print("\nExample 2: Negation and Dependency Relations in CVC5")
    pyetr_formula = "∀x {~S(x)T(x), ~S(x)~T(x)} ^ {~S(x*)}"
    print("Inspired PyETR Formula:", pyetr_formula)

    solver = cvc5.Solver()
    solver.setOption("produce-models", "true")
    solver.setLogic("ALL")

    bool_sort = solver.getBooleanSort()

    S = solver.mkConst(bool_sort, "S")
    T = solver.mkConst(bool_sort, "T")
    x = solver.mkVar(bool_sort, "x")

    not_s = solver.mkTerm(cvc5.Kind.NOT, S)
    not_t = solver.mkTerm(cvc5.Kind.NOT, T)
    inner_term = solver.mkTerm(cvc5.Kind.EQUAL, not_s, not_t)
    bound_vars = solver.mkTerm(cvc5.Kind.VARIABLE_LIST, x)
    forall_x = solver.mkTerm(cvc5.Kind.FORALL, bound_vars, inner_term)
    solver.assertFormula(forall_x)

    print("Expression (CVC5 representation):", str(forall_x))
    print("Expression (string representation):", str(forall_x))

    result = solver.checkSat()
    if result.isSat():
        print("Satisfiable. Model:")
        print(solver.getValue(S))
        print(solver.getValue(T))
    else:
        print("Unsatisfiable")


def example_3():
    print("\nExample 3: Weighted States in CVC5")
    pyetr_formula = "∀x {0.3=* P(x*)C(x), P(x*)~C(x)} ^ {P(x*)}"
    print("Inspired PyETR Formula:", pyetr_formula)

    solver = cvc5.Solver()
    solver.setOption("produce-models", "true")
    solver.setLogic("ALL")

    real_sort = solver.getRealSort()

    P = solver.mkConst(real_sort, "P")
    C = solver.mkConst(real_sort, "C")
    x = solver.mkVar(real_sort, "x")

    weight = solver.mkReal(0.3)
    mult_expr = solver.mkTerm(cvc5.Kind.MULT, weight, C)
    inner_term = solver.mkTerm(cvc5.Kind.EQUAL, P, mult_expr)
    bound_vars = solver.mkTerm(cvc5.Kind.VARIABLE_LIST, x)
    forall_x = solver.mkTerm(cvc5.Kind.FORALL, bound_vars, inner_term)
    solver.assertFormula(forall_x)

    print("Expression (CVC5 representation):", str(forall_x))
    print("Expression (string representation):", str(forall_x))

    result = solver.checkSat()
    if result.isSat():
        print("Satisfiable. Model:")
        print(solver.getValue(P))
        print(solver.getValue(C))
    else:
        print("Unsatisfiable")


if __name__ == "__main__":
    example_1()
    example_2()
    example_3()
