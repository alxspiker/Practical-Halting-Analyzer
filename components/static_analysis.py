# File: components/static_analysis.py
import ast

class RecursionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.call_graph = {}
        self.current_func = None

    def visit_FunctionDef(self, node):
        self.current_func = node.name
        self.call_graph[self.current_func] = set()
        self.generic_visit(node)
        self.current_func = None

    def visit_Call(self, node):
        if self.current_func and isinstance(node.func, ast.Name):
            self.call_graph[self.current_func].add(node.func.id)
        self.generic_visit(node)

def has_infinite_recursion(call_graph):
    # Simple cycle detection for recursion without base case
    for func in call_graph:
        if func in call_graph[func]:  # Direct recursion
            # Check if there's a base case; this is heuristic
            return True  # Assume no base case for simplicity; enhance later
        # For mutual, check cycles
        visited = set()
        stack = [func]
        while stack:
            node = stack[-1]
            if node not in visited:
                visited.add(node)
                for child in call_graph.get(node, []):
                    if child in stack:
                        return True  # Cycle detected
                    stack.append(child)
            else:
                stack.pop()
    return False

def static_preparation(program: str) -> tuple[str, str]:
    """
    Phase 1: Static analysis to find obvious halting or non-halting cases.
    Returns a tuple of (result, reason).
    """
    try:
        tree = ast.parse(program)
        
        has_loops = False
        has_recursion = False
        infinite_loop_detected = False

        for node in ast.walk(tree):
            # Check for any kind of loop
            if isinstance(node, (ast.For, ast.While)):
                has_loops = True
                # Check for definitive non-halting cases
                if isinstance(node, ast.While):
                    if isinstance(node.test, ast.Constant) and node.test.value is True:
                        infinite_loop_detected = True
                    else:
                        # Check if condition can change
                        modified_vars = set()
                        for body_node in ast.walk(node):
                            if isinstance(body_node, ast.Assign):
                                for target in body_node.targets:
                                    if isinstance(target, ast.Name):
                                        modified_vars.add(target.id)
                        # If loop test vars not modified, infinite
                        if isinstance(node.test, ast.Compare):
                            vars_in_test = set()
                            for comp_node in ast.walk(node.test):
                                if isinstance(comp_node, ast.Name):
                                    vars_in_test.add(comp_node.id)
                            if not vars_in_test.intersection(modified_vars):
                                infinite_loop_detected = True
            
            # Check for recursion
            elif isinstance(node, ast.FunctionDef):
                recursion_visitor = RecursionVisitor()
                recursion_visitor.visit(tree)
                if has_infinite_recursion(recursion_visitor.call_graph):
                    has_recursion = True
        
        if infinite_loop_detected:
            return "does not halt", "Static analysis: Detected an infinite loop (condition unchanged or always true)."

        # The most definitive halting case: a program with no loops and no recursion.
        if not has_loops and not has_recursion:
            return "halts", "Static analysis: Program has no loops or recursion, so it must halt."

        # If we have found loops (that aren't infinite) or recursion, defer.
        return "impossible to determine", "Static analysis: Program contains complex loops or recursion that could not be proven to terminate."

    except SyntaxError:
        return "impossible to determine", "Static analysis: Could not parse the script due to a syntax error."
    except Exception as e:
        return "impossible to determine", f"Static analysis: An unexpected error occurred: {str(e)}"