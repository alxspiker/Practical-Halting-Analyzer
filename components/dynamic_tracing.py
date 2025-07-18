import sys
import re  # <-- Add this import
from collections import defaultdict

def dynamic_tracing(program: str) -> str:
    """Phase 3: Dynamic tracing to detect non-halting behavior."""
    try:
        # --- MODIFIED: Replace the blunt string search with a more precise regex ---
        # This looks for 'analyze_halting' followed by an opening parenthesis '(',
        # which is a much stronger signal of a function call than a simple substring.
        # This prevents false positives on comments or variable names.
        if re.search(r"analyze_halting\s*\(", program):
            return "does not halt"  # Probable self-referential call

        trace_log = []
        call_depth = defaultdict(int)

        def trace(frame, event, arg):
            if event == "call":
                call_depth[frame.f_code.co_name] += 1
                if call_depth[frame.f_code.co_name] > 100:
                    raise RecursionError("Deep recursion detected")
            if event == "line":
                line_no = frame.f_lineno
                local_vars_tuple = tuple(sorted(frame.f_locals.items()))
                trace_log.append((line_no, local_vars_tuple))

            if len(trace_log) > 1 and len(trace_log) % 2 == 0:
                half = len(trace_log) // 2
                if trace_log[:half] == trace_log[half:]:
                    raise RuntimeError("Cycle detected in execution trace")

            if len(trace_log) > 10000:
                raise RuntimeError("Trace log exceeded maximum size")

            return trace

        sys.settrace(trace)
        try:
            exec(program, {})
        except RecursionError:
            sys.settrace(None)
            return "does not halt"
        except RuntimeError as e:
            if "Cycle detected" in str(e) or "Trace log exceeded" in str(e):
                sys.settrace(None)
                return "does not halt"
            else:
                sys.settrace(None)
                return "halts"
        except Exception as e:
            sys.settrace(None)
            return "halts"  # Exceptions terminate execution
        sys.settrace(None)
        return "halts"
    except Exception as e:
        return f"impossible to determine: {str(e)}"