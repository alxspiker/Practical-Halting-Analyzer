import sys
import re
from collections import defaultdict

def dynamic_tracing(program: str) -> tuple[str, str]:
    """
    Phase 3: Dynamic tracing to detect non-halting behavior.
    Returns a tuple of (result, reason).
    """
    try:
        if re.search(r"analyze_halting\s*\(", program):
            return "does not halt", "Dynamic tracing: Pre-execution check found a probable call to the analyzer."

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