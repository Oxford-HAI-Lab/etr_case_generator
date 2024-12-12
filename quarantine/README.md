# PyETR Formula Handling Investigation

This outlines several investigations into libraries that can work with first order logic. My question is: which of these libraries can help us generate random logical statements for evals? I found that generating statements [with our own code](../lm_eval/data_generation/random_logical/generate_random_questions.py) was getting pretty clunky, and I think one of these libraries can help us out.

You can look at the files to see what the code is like. Basically here's a summary:

![image](https://github.com/user-attachments/assets/d92a56b6-b4cf-4221-807f-bcb66fc7acdc)

# Z3 ([try_z3.py](try_z3.py))

Install with:
```bash
pip install z3-solver
```

Run with:
```bash
python try_z3.py
```

Example code:

```python
    print("PyETR: ∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}")
    Student = Bool('Student')
    Reads = Bool('Reads')
    Book = Bool('Book')
    z = Bool('z')
    w = Bool('w')
    expr = ForAll([z], Exists([w], Reads == Book))
    solver = Solver()
    solver.add(expr)
```

Example output:
```
Example 1: Quantified View in Z3
PyETR: ∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}
Expression (Z3 representation): ForAll(z, Exists(w, Reads == Book))
Expression (string representation): ForAll(z, Exists(w, Reads == Book))
Expression (raw format): (forall ((z Bool)) (exists ((w Bool)) (= Reads Book)))
Satisfiable. Model: [Book = False, Reads = False]

Example 2: Negation and Dependency Relations in Z3
PyETR: ∀x {~S(x)T(x), ~S(x)~T(x)} ^ {~S(x*)}
Expression (Z3 representation): ForAll(x, S == Not(T))
Expression (string representation): ForAll(x, S == Not(T))
Expression (raw format): (forall ((x Bool)) (= S (not T)))
Satisfiable. Model: [S = False, T = True]

Example 3: Weighted States in Z3
PyETR: ∀x {0.3=* P(x*)C(x), P(x*)~C(x)} ^ {P(x*)}
Expression (Z3 representation): ForAll(x, P == 3/10*C)
Expression (string representation): ForAll(x, P == 3/10*C)
Expression (raw format): (forall ((x Real)) (= P (* (/ 3.0 10.0) C)))
Satisfiable. Model: [C = 0, P = 0]
```

# PySMT ([try_smt.py](try_smt.py))

PySMT provides a unified interface to several SMT solvers, including Z3 which it uses as its default backend. It offers a more Pythonic API compared to direct Z3 usage, while maintaining the same solving capabilities. This makes it particularly attractive for Python-centric projects.

Install with:
```bash
pip install pysmt
```

After installation, you'll need to install at least one solver backend:
```bash
pysmt-install --z3
```

Run with:
```bash
python try_smt.py
```

Example code:

```python
    pyetr_formula = "∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}"
    
    Student = Symbol("Student", BOOL)
    Reads = Symbol("Reads", BOOL)
    Book = Symbol("Book", BOOL)
    z1 = Symbol("z1", BOOL)
    w1 = Symbol("w1", BOOL)

    expr = ForAll([z1], Exists([w1], Reads.Iff(Book)))
    with Solver() as solver:
        solver.add_assertion(expr)
```

Example output:
```
Example 1: Quantified View in PySMT
Inspired PyETR Formula: ∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}
Expression (PySMT representation): (forall z1 . (exists w1 . (Reads <-> Book)))
Expression (string representation): (forall z1 . (exists w1 . (Reads <-> Book)))
Satisfiable. Model: Book := False
Reads := False

Example 2: Negation and Dependency Relations in PySMT
Inspired PyETR Formula: ∀x {~S(x)T(x), ~S(x)~T(x)} ^ {~S(x*)}
Expression (PySMT representation): (forall x2 . ((! S) <-> (! T)))
Expression (string representation): (forall x2 . ((! S) <-> (! T)))
Satisfiable. Model: S := False
T := False

Example 3: Weighted States in PySMT
Inspired PyETR Formula: ∀x {0.3=* P(x*)C(x), P(x*)~C(x)} ^ {P(x*)}
Expression (PySMT representation): (forall x3 . (P = (5404319552844595/18014398509481984 * C)))
Expression (string representation): (forall x3 . (P = (5404319552844595/18014398509481984 * C)))
Satisfiable. Model: C := 0.0
P := 0.0
```

# CVC5 ([try_cvc5.py](try_cvc5.py))

Install with:
```bash
pip install cvc5
```

Run with:
```bash
python try_cvc5.py
```

Example code:

```python
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
```

Example output:
```
Example 1: Quantified View in CVC5
Inspired PyETR Formula: ∀z ∃w {Student(z*)Reads(z,w)Book(w)}^{Student(z*)}
Expression (CVC5 representation): (forall ((z Bool)) (exists ((w Bool)) (= Reads Book)))
Expression (string representation): (forall ((z Bool)) (exists ((w Bool)) (= Reads Book)))

Example 2: Negation and Dependency Relations in CVC5
Inspired PyETR Formula: ∀x {~S(x)T(x), ~S(x)~T(x)} ^ {~S(x*)}
Expression (CVC5 representation): (forall ((x Bool)) (= (not S) (not T)))
Expression (string representation): (forall ((x Bool)) (= (not S) (not T)))

Example 3: Weighted States in CVC5
Inspired PyETR Formula: ∀x {0.3=* P(x*)C(x), P(x*)~C(x)} ^ {P(x*)}
Expression (CVC5 representation): (forall ((x Real)) (= P (* (/ 3 10) C)))
Expression (string representation): (forall ((x Real)) (= P (* (/ 3 10) C)))
```

# SymPy ([generate_random_questions_sympy.py](../lm_eval/data_generation/random_logical/generate_random_questions_sympy.py))

Although SymPy is widely used, it lacks support for full First Order Logic, only supporting predicate logic. Sadly, it is really suitable only for propositional logic.

Install with:
```bash
pip install sympy
```

Run with:
```bash
python try_sympy.py
```

Example code:

```python
    x1, x2, x3, x4 = symbols('x1 x2 x3 x4')
    statement = ~x3 & (x1 | x4 | (x1 & ~(x4 | ~x2 | ~(x2 | x3))))
    cnf = to_cnf(statement)
    dnf = to_dnf(statement)
    natural_language = str(statement)
    necessary_assignments = necessary_assignments(statement)
    follows = follows(statement)
    num_clauses = len(cnf.args)
    num_variables = len(statement.free_symbols)
```

Example output:
```
Question 1:
Statement: ~x3 & (x1 | x4 | (x1 & ~(x4 | ~x2 | ~(x2 | x3))))
CNF: ~x3 & (x1 | x4) & (x1 | x2 | x4) & (x1 | x4 | ~x4) & (x1 | x2 | x3 | x4)
DNF: (x1 & ~x3) | (x4 & ~x3) | (x1 & x2 & ~x3 & ~x4) | (x1 & x2 & x3 & ~x3 & ~x4)
Natural Language: not x3 and (x1 or x4 or (x1 and not (x4 or not x2 or not (x2 or x3))))
Necessary Assignments:
  x4: None
  x3: False
  x1: None
  x2: None
Follows:
  - x3 is False
Number of Clauses: 3
Number of Variables: 4

Question 2:
Statement: x3 & ~x1 & (x3 | (~x2 & (x4 | (x4 & (x1 | x2 | x4 | ~x2)))))
CNF: x3 & ~x1 & (x3 | x4) & (x3 | ~x2) & (x1 | x2 | x3 | x4 | ~x2)
DNF: (x3 & ~x1) | (x3 & x4 & ~x1 & ~x2) | (x1 & x3 & x4 & ~x1 & ~x2) | (x2 & x3 & x4 & ~x1 & ~x2)
Natural Language: x3 and not x1 and (x3 or (not x2 and (x4 or (x4 and (x1 or x2 or x4 or not x2)))))
Necessary Assignments:
  x4: None
  x1: False
  x3: True
  x2: None
Follows:
  - x1 is False
  - x3 is True
Number of Clauses: 3
Number of Variables: 4

Example of a random logical expression:
Original expression: x2 | ~x4 | (x2 & x3)
Simplified (simplify): x2 | ~x4
Simplified (simplify_logic): x2 | ~x4
CNF: (x2 | ~x4) & (x2 | x3 | ~x4)
DNF: x2 | ~x4 | (x2 & x3)
Natural Language: x2 or not x4 or (x2 and x3)
```

