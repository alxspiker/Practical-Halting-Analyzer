import ast

def static_preparation(program: str) -> tuple[str, str]:
    """
    Phase 1: Static analysis to find obvious halting or non-halting cases.
    Returns a tuple of (result, reason).
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
                if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
                    return "does not halt", "Static analysis: Detected a 'while True' infinite loop."
            
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
            return "halts", "Static analysis: Program has no loops or recursion, so it must halt."

        # If we have found loops (that aren't `while True`) or recursion, defer.
        return "impossible to determine", "Static analysis: Program contains complex loops or recursion that could not be proven to terminate."

    except SyntaxError:
        return "impossible to determine", "Static analysis: Could not parse the script due to a syntax error."
    except Exception as e:
        return "impossible to determine", f"Static analysis: An unexpected error occurred: {str(e)}"