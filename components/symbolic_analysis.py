import ast
from z3 import Solver, Int, sat, Not, And, Or

def parse_update(body, var_name):
    """Parses the loop body to find how the loop variable is updated."""
    for stmt in body:
        # Handle `x = x - 1`
        if (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name) and
                stmt.targets[0].id == var_name and isinstance(stmt.value, ast.BinOp)):
            op = stmt.value.op
            right = stmt.value.right
            if isinstance(right, ast.Constant):
                if isinstance(op, ast.Sub):
                    return lambda v: v - right.n
                elif isinstance(op, ast.Add):
                    return lambda v: v + right.n
    return None # No simple update found

def symbolic_analysis(program: str) -> str:
    """
    Phase 2: Symbolic analysis using Z3 to prove loop termination.
    Attempts to find a ranking function for simple loops by parsing the body.
    """
    try:
        tree = ast.parse(program)
        s = Solver()

        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                if not (isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Gt)):
                    continue # Only handle simple `var > const` conditions for now

                var_name = node.test.left.id
                loop_var = Int(var_name)
                
                # Model the loop condition
                condition = loop_var > 0 
                
                # Model the loop body's effect by parsing it
                update_func = parse_update(node.body, var_name)
                if not update_func:
                    continue # Could not model the update
                
                loop_var_prime = Int(f"{var_name}'")
                update_relation = (loop_var_prime == update_func(loop_var))

                # Define ranking function V(x) = x
                ranking_function = loop_var

                # Prove termination properties
                s.push()
                # 1. Ranking function must be non-negative when loop condition is true
                s.add(And(condition, ranking_function < 0))
                if s.check() == sat:
                    s.pop()
                    continue

                # 2. Each iteration under the condition must strictly decrease the ranking function
                s.add(And(condition, update_relation, ranking_function <= loop_var_prime))
                if s.check() == sat:
                    s.pop()
                    continue 

                s.pop()
                return "halts" # Proved termination

        return "impossible to determine"
    except Exception:
        return "impossible to determine"