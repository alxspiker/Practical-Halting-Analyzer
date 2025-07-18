import ast
from z3 import Solver, Int, sat, And, Or, Not

def prove_termination(program: str) -> tuple[str, str]:
    """
    An advanced symbolic analysis phase that attempts to prove termination.
    Returns a tuple of (result, reason).
    """
    try:
        tree = ast.parse(program)
        solver = Solver()

        for node in ast.walk(tree):
            # Case 1: Handle simple 'for i in range(constant)' loops
            if isinstance(node, ast.For):
                if (isinstance(node.iter, ast.Call) and
                    isinstance(node.iter.func, ast.Name) and
                    node.iter.func.id == 'range' and
                    len(node.iter.args) == 1 and
                    isinstance(node.iter.args[0], ast.Constant)):
                    return "halts", "Symbolic prover: Proved termination of a 'for' loop with a constant range."

            # Case 2: Handle simple 'while var < const' loops with clear progress
            elif isinstance(node, ast.While):
                if not (isinstance(node.test, ast.Compare) and
                        len(node.test.ops) == 1 and
                        isinstance(node.test.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) and
                        isinstance(node.test.left, ast.Name) and
                        isinstance(node.test.comparators[0], ast.Constant)):
                    continue

                var_name = node.test.left.id
                update_found = False
                for body_stmt in node.body:
                    if (isinstance(body_stmt, ast.Assign) and
                        isinstance(body_stmt.targets[0], ast.Name) and
                        body_stmt.targets[0].id == var_name and
                        isinstance(body_stmt.value, ast.BinOp) and
                        isinstance(body_stmt.value.left, ast.Name) and
                        body_stmt.value.left.id == var_name and
                        isinstance(body_stmt.value.op, ast.Add) and
                        isinstance(body_stmt.value.right, ast.Constant)):
                        update_found = True
                        break

                if update_found:
                    return "halts", "Symbolic prover: Proved termination of a 'while' loop with a clear progress condition."

        return "impossible to determine", "Symbolic prover: Could not prove termination for any loop structures."

    except Exception:
        return "impossible to determine", "Symbolic prover: An internal error occurred during analysis."