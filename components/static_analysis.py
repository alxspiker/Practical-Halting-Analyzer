import ast

def is_constant_true(node):
    """Check if an AST node is a constant True value."""
    return isinstance(node, ast.Constant) and node.value is True

def static_preparation(program: str) -> str:
    """
    Phase 1: Static analysis to find obvious halting or non-halting cases.
    - Detects `while True` loops for non-halting.
    - NEW: Detects recursive function calls as a form of non-trivial complexity.
    - Confirms halting only if NO loops AND NO recursion are present.
    """
    try:
        tree = ast.parse(program)
        
        has_loops = False
        has_recursion = False

        for node in ast.walk(tree):
            # Check for any kind of loop
            if isinstance(node, (ast.For, ast.While)):
                has_loops = True
                # Check for the definitive non-halting case
                if isinstance(node, ast.While) and is_constant_true(node.test):
                    return "does not halt"
            
            # Check for any function that calls itself
            elif isinstance(node, ast.FunctionDef):
                function_name = node.name
                # Walk the body of this specific function
                for body_node in ast.walk(node):
                    if (isinstance(body_node, ast.Call) and 
                        isinstance(body_node.func, ast.Name) and 
                        body_node.func.id == function_name):
                        has_recursion = True
                        break # Found recursion in this function, no need to check further
                if has_recursion:
                    break # Found recursion in the program, no need to check other functions
        
        # The most definitive halting case: a program with no loops and no recursion.
        if not has_loops and not has_recursion:
            return "halts"

        # If we have found loops (that aren't `while True`) or recursion,
        # the program is too complex for a simple static decision. Defer.
        return "impossible to determine"

    except SyntaxError:
        return "impossible to determine: syntax error"
    except Exception as e:
        return f"impossible to determine: {str(e)}"