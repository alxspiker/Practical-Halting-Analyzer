import ast

def is_constant_true(node):
    """Check if an AST node is a constant True value."""
    return isinstance(node, ast.Constant) and node.value is True

def static_preparation(program: str) -> str:
    """
    Phase 1: Static analysis to find obvious halting or non-halting cases.
    - Detects `while True` loops for non-halting.
    - Detects simple bounded `for` loops to confirm halting if no other loops exist.
    """
    try:
        tree = ast.parse(program)
        
        has_unbounded_loop = False
        has_loops = False

        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                has_loops = True
                if is_constant_true(node.test):
                    # Found a `while True`, which is a definitive non-halting case.
                    return "does not halt"
                else:
                    # Any other `while` loop is considered potentially unbounded.
                    has_unbounded_loop = True
            elif isinstance(node, ast.For):
                has_loops = True
                # Simple check for bounded iteration over range().
                # This is an oversimplification but better than nothing.
                if not (isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range'):
                    has_unbounded_loop = True

        if not has_loops:
            # If there are no loops at all, the program must halt.
            return "halts"

        if not has_unbounded_loop:
            # All loops found were determined to be bounded (e.g., simple for loops).
            return "halts"

        # If we found potentially unbounded loops but no `while True`, defer the decision.
        return "impossible to determine"

    except SyntaxError:
        return "impossible to determine: syntax error"
    except Exception as e:
        return f"impossible to determine: {str(e)}"