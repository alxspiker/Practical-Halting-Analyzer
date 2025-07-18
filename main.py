import argparse
import sys
import hashlib
from components.paradox_detection import detect_paradox
from components.static_analysis import static_preparation
from components.symbolic_analysis import symbolic_analysis
from components.dynamic_tracing import dynamic_tracing
from components.decision_synthesis import decision_synthesis

# --- MODIFIED: Import the new cross-script recursion detector ---
from components.cross_script_recursion import start_analysis, end_analysis, RecursionCycleDetected

# --- REMOVED: The old ANALYSIS_STACK set is no longer needed ---
# ANALYSIS_STACK = set()

def analyze_halting(program: str) -> str:
    """Analyze if a program halts using a four-phase approach."""
    program_hash = hashlib.sha256(program.encode('utf-8')).hexdigest()

    try:
        # --- MODIFIED: Use the new chain detector ---
        # This will check for both direct (A->A) and mutual (A->B->A) recursion.
        start_analysis(program_hash)

    except RecursionCycleDetected as e:
        # The new component found a cycle. This is a non-halting condition.
        print(f"Debug: {str(e)}", file=sys.stderr)
        return "does not halt"

    try:
        # The main analysis logic remains wrapped in a try/finally block
        # to ensure end_analysis is always called.
        if detect_paradox(program):
            print("Debug: Detected potential halting paradox", file=sys.stderr)
            return "impossible to determine: detected potential halting paradox"
        
        # Phase 1: Static Preparation
        static_result = static_preparation(program)
        print(f"Debug: Static result = {static_result}", file=sys.stderr)
        if static_result == "halts":
            return "halts"
        if static_result == "does not halt":
            return "does not halt"
        
        # Phase 2: Symbolic Analysis
        symbolic_result = symbolic_analysis(program)
        print(f"Debug: Symbolic result = {symbolic_result}", file=sys.stderr)
        if symbolic_result in ["halts", "does not halt"]:
            return symbolic_result
        
        # Phase 3: Dynamic Tracing
        dynamic_result = dynamic_tracing(program)
        print(f"Debug: Dynamic result = {dynamic_result}", file=sys.stderr)
        if dynamic_result in ["halts", "does not halt"]:
            return dynamic_result
        
        # Phase 4: Decision Synthesis
        final_result = decision_synthesis(static_result, symbolic_result, dynamic_result, program)
        print(f"Debug: Final result = {final_result}", file=sys.stderr)
        return final_result
        
    except Exception as e:
        print(f"Debug: Exception = {str(e)}", file=sys.stderr)
        return f"impossible to determine: {str(e)}"
    finally:
        # --- MODIFIED: Ensure we call the new end_analysis function ---
        end_analysis(program_hash)

if __name__ == "__main__":
    import os
    import sys

    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
    print(f"--- Running Halting Analysis on all scripts in '{scripts_dir}' ---")

    for script_name in sorted(os.listdir(scripts_dir)):
        if script_name.endswith('.py'):
            script_path = os.path.join(scripts_dir, script_name)
            print(f"\n[Analyzing]: {script_name}")
            print("-" * (12 + len(script_name)))
            
            try:
                with open(script_path, 'r') as f:
                    program_code = f.read()
                
                result = analyze_halting(program_code)
                print(f"Result: {result}")
                print("-" * (12 + len(script_name)))

            except Exception as e:
                print(f"Error analyzing {script_name}: {e}", file=sys.stderr)
    
    print("\n--- Analysis Complete ---")