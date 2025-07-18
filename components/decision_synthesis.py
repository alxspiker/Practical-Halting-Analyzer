# File: components/decision_synthesis.py
import re
import ast

def decision_synthesis(static_result: str, symbolic_result: str, dynamic_result: str, program: str) -> str:
    """Phase 4: Synthesize results from prior phases and handle self-reference."""
    try:
        # Prioritize definitive static or symbolic results
        if static_result in ["halts", "does not halt"]:
            return static_result
        if symbolic_result in ["halts", "does not halt"]:
            return symbolic_result
        if dynamic_result in ["halts", "does not halt"]:
            return dynamic_result
        
        # Weighted voting
        votes = {'halts': 0, 'does not halt': 0, 'impossible to determine': 0}
        confidences = {'static': 0.8, 'symbolic': 0.7, 'dynamic': 0.6}
        
        for phase, result in [('static', static_result), ('symbolic', symbolic_result), ('dynamic', dynamic_result)]:
            if result != 'continue' and result != 'impossible to determine':
                votes[result] += confidences.get(phase, 0.5)
        
        max_vote = max(votes, key=votes.get)
        if votes[max_vote] > 1.0:  # Threshold for confidence
            return max_vote
        
        # Self-reference detection using AST
        tree = ast.parse(program)
        has_self_read = False
        has_analyzer_call = False
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                if len(node.items) == 1 and isinstance(node.items[0].context_expr, ast.Call) and node.items[0].context_expr.func.id == 'open':
                    if isinstance(node.items[0].context_expr.args[0], ast.Name) and node.items[0].context_expr.args[0].id == '__file__':
                        has_self_read = True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'analyze_halting':
                has_analyzer_call = True
        
        if has_self_read and has_analyzer_call:
            return "does not halt"
        
        # Check for self-reference in program text as fallback
        if "analyze_halting" in program:
            return "does not halt"
        
        # If all phases are inconclusive
        return "impossible to determine"
    except Exception as e:
        return f"impossible to determine: {str(e)}"