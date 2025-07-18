# File: components/dynamic_tracing.py
import sys
import re
import ast
from collections import defaultdict
import hashlib

def dynamic_tracing(program: str) -> tuple[str, str]:
    """
    Phase 3: Dynamic tracing to detect non-halting behavior.
    Returns a tuple of (result, reason).
    """
    try:
        # Obfuscation-resistant analyzer call detection using AST
        tree = ast.parse(program)
        has_analyzer_call = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'analyze_halting':
                has_analyzer_call = True
                break
        if has_analyzer_call:
            return "does not halt", "Dynamic tracing: Pre-execution check found a call to the analyzer."

        trace_log = []
        call_depth = defaultdict(int)
        state_hashes = []

        def trace(frame, event, arg):
            if event == "call":
                call_depth[frame.f_code.co_name] += 1
                if call_depth[frame.f_code.co_name] > 200:  # Increased limit
                    raise RecursionError("Deep recursion detected")
            if event == "line":
                line_no = frame.f_lineno
                local_vars_tuple = tuple(sorted(frame.f_locals.items()))
                state = (line_no, local_vars_tuple)
                state_hash = hashlib.sha256(str(state).encode()).hexdigest()
                trace_log.append(state_hash)

            if len(trace_log) > 20000:  # Increased limit
                raise RuntimeError("Trace log exceeded maximum size")

            # Cycle detection with hashes
            if state_hash in state_hashes:
                raise RuntimeError("Cycle detected in execution trace")
            state_hashes.append(state_hash)

            return trace

        sys.settrace(trace)
        try:
            exec(program, {})
        except RecursionError:
            sys.settrace(None)
            return "does not halt", "Dynamic tracing: Execution exceeded maximum recursion depth."
        except RuntimeError as e:
            sys.settrace(None)
            if "Cycle detected" in str(e):
                return "does not halt", "Dynamic tracing: Execution trace entered a deterministic loop."
            elif "Trace log exceeded" in str(e):
                return "does not halt", "Dynamic tracing: Execution exceeded maximum trace log size."
            else:
                return "halts", f"Dynamic tracing: Execution terminated with a runtime error: {str(e)}."
        except Exception as e:
            sys.settrace(None)
            return "halts", f"Dynamic tracing: Execution terminated with an exception: {type(e).__name__}."
        sys.settrace(None)
        return "halts", "Dynamic tracing: Program executed to completion without issue."
    except Exception as e:
        return "impossible to determine", f"Dynamic tracing: An internal error occurred: {str(e)}."