import re

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
        # Check for self-reference in program text
        if "analyze_halting" in program:
            return "does not halt"
        # If all phases are inconclusive
        return "impossible to determine"
    except Exception as e:
        return f"impossible to determine: {str(e)}"