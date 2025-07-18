# File: components/heuristic_classifier.py
import ast
import difflib

class CollatzVisitor(ast.NodeVisitor):
    """
    Looks for the specific structure of the Collatz conjecture algorithm.
    This version correctly inspects the body of the while loop.
    """
    def __init__(self):
        self.is_collatz_like = False

    def visit_While(self, node):
        # 1. Check for the `while n != 1` loop condition
        if not (isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                isinstance(node.test.ops[0], ast.NotEq) and
                isinstance(node.test.comparators[0], ast.Constant) and
                node.test.comparators[0].value == 1):
            self.generic_visit(node)
            return

        var_name = node.test.left.id
        if_stmt = None
        
        # 2. Find the primary If statement inside the loop's body
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                if_stmt = stmt
                break
        
        if if_stmt is None:
            self.generic_visit(node)
            return

        # 3. Check if the test is `if n % 2 == 0`
        found_even_check = (isinstance(if_stmt.test, ast.Compare) and
                            isinstance(if_stmt.test.left, ast.BinOp) and
                            isinstance(if_stmt.test.left.left, ast.Name) and
                            if_stmt.test.left.left.id == var_name and
                            isinstance(if_stmt.test.left.op, ast.Mod) and
                            isinstance(if_stmt.test.ops[0], ast.Eq) and
                            isinstance(if_stmt.test.comparators[0], ast.Constant) and
                            if_stmt.test.comparators[0].value == 0)

        if not found_even_check:
            self.generic_visit(node)
            return

        # 4. Check for `n = n // 2` in the 'if' body
        found_even_update = False
        for stmt in if_stmt.body:
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and
                isinstance(stmt.targets[0], ast.Name) and stmt.targets[0].id == var_name and
                isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, ast.FloorDiv)):
                found_even_update = True
                break
        
        # 5. Check for `n = 3 * n + 1` in the 'else' body
        found_odd_update = False
        for stmt in if_stmt.orelse:
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and
                isinstance(stmt.targets[0], ast.Name) and stmt.targets[0].id == var_name and
                isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, ast.Add) and
                isinstance(stmt.value.left, ast.BinOp) and isinstance(stmt.value.left.op, ast.Mult)):
                found_odd_update = True
                break
        
        if found_even_update and found_odd_update:
            self.is_collatz_like = True
        
        # We have analyzed this loop, no need to visit its children.
        return


class AckermannVisitor(ast.NodeVisitor):
    """
    Looks for the specific recursive structure of the Ackermann function.
    This version correctly traverses the if/elif/elif structure.
    """
    def __init__(self):
        self.is_ackermann_like = False

    def visit_FunctionDef(self, node):
        # Must be a function with exactly two arguments
        if len(node.args.args) != 2:
            self.generic_visit(node)
            return

        func_name, m_arg, n_arg = node.name, node.args.args[0].arg, node.args.args[1].arg
        
        # The function body must start with an If statement
        if not (node.body and isinstance(node.body[0], ast.If)):
            self.generic_visit(node)
            return
            
        if_stmt1 = node.body[0]

        # Case 1: Check for `if m == 0:`
        case1_ok = (self._is_comparison(if_stmt1.test, m_arg, ast.Eq, 0) and
                    if_stmt1.body and isinstance(if_stmt1.body[0], ast.Return))
        if not case1_ok:
            self.generic_visit(node)
            return

        # The 'orelse' block contains the 'elif' part
        if not (if_stmt1.orelse and isinstance(if_stmt1.orelse[0], ast.If)):
            self.generic_visit(node)
            return
        if_stmt2 = if_stmt1.orelse[0]
        
        # Case 2: Check for `elif m > 0 and n == 0:` and the single recursive call
        case2_test_ok = isinstance(if_stmt2.test, ast.BoolOp)
        case2_body_ok = False
        if if_stmt2.body and isinstance(if_stmt2.body[0], ast.Return):
            ret_val = if_stmt2.body[0].value
            case2_body_ok = (isinstance(ret_val, ast.Call) and
                             isinstance(ret_val.func, ast.Name) and ret_val.func.id == func_name and
                             # check for the inner call being non-recursive
                             len(ret_val.args) == 2 and not isinstance(ret_val.args[1], ast.Call))
        if not (case2_test_ok and case2_body_ok):
            self.generic_visit(node)
            return
            
        # The next 'orelse' block contains the final 'elif'
        if not (if_stmt2.orelse and isinstance(if_stmt2.orelse[0], ast.If)):
            self.generic_visit(node)
            return
        if_stmt3 = if_stmt2.orelse[0]
        
        # Case 3: Check for `elif m > 0 and n > 0:` and the double recursive call
        case3_test_ok = isinstance(if_stmt3.test, ast.BoolOp)
        case3_body_ok = False
        if if_stmt3.body and isinstance(if_stmt3.body[0], ast.Return):
            ret_val = if_stmt3.body[0].value
            if (isinstance(ret_val, ast.Call) and
                isinstance(ret_val.func, ast.Name) and ret_val.func.id == func_name and
                len(ret_val.args) == 2 and
                isinstance(ret_val.args[1], ast.Call) and # The inner call
                isinstance(ret_val.args[1].func, ast.Name) and ret_val.args[1].func.id == func_name):
                case3_body_ok = True

        if case3_test_ok and case3_body_ok:
            self.is_ackermann_like = True
        
        # We've processed this function, so we can stop visiting its children
        return
        
    def _is_comparison(self, node, var_name, op, val):
        return (isinstance(node, ast.Compare) and
                isinstance(node.left, ast.Name) and node.left.id == var_name and
                isinstance(node.ops[0], op) and
                isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value == val)

# Known patterns for hard problems
KNOWN_HARD_PATTERNS = [
    # Busy Beaver example
    """
def busy_beaver():
    tape = [0] * 100
    state = 0
    pos = 0
    while state != 'halt':
        # Simulate TM
        pass
""",
    # Turing machine simulation
    """
class TuringMachine:
    def run(self):
        while True:
            # state transitions
            pass
"""
]

def is_similar_to_known(code, pattern, threshold=0.8):
    seq_matcher = difflib.SequenceMatcher(None, code, pattern)
    return seq_matcher.ratio() > threshold

def classify_known_problems(program: str) -> tuple[str, str]:
    """
    Phase 1.5: Heuristically check for known hard problems.
    Returns a tuple of (result, reason).
    """
    try:
        tree = ast.parse(program)
        
        collatz_visitor = CollatzVisitor()
        collatz_visitor.visit(tree)
        if collatz_visitor.is_collatz_like:
            return "impossible to determine", "Heuristic classification: Detected a structure matching the Collatz conjecture."

        ackermann_visitor = AckermannVisitor()
        ackermann_visitor.visit(tree)
        if ackermann_visitor.is_ackermann_like:
            return "impossible to determine", "Heuristic classification: Detected a structure matching the Ackermann function."

        # Check for other known hard patterns using fuzzy matching
        for pattern in KNOWN_HARD_PATTERNS:
            if is_similar_to_known(program, pattern):
                return "impossible to determine", "Heuristic classification: Detected a structure similar to a known undecidable problem (e.g., Busy Beaver or Turing machine)."
            
    except Exception:
        # If parsing or classification fails, defer the decision.
        return "continue", ""
        
    return "continue", ""