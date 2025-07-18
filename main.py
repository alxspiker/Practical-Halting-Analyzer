import argparse
import sys
import os
from components.paradox_detection import detect_paradox
from components.static_analysis import static_preparation
# --- NEW: Import the heuristic classifier ---
from components.heuristic_classifier import classify_known_problems
from components.symbolic_prover import prove_termination
from components.dynamic_tracing import dynamic_tracing
from components.decision_synthesis import decision_synthesis
from components.cross_script_recursion import start_analysis, end_analysis, RecursionCycleDetected
from components.semantic_hashing import get_semantic_hash

# This function is now designed to be imported and used by other scripts.
def analyze_halting(program: str) -> str:
    """Analyze if a program halts using a multi-phase approach."""
    program_hash = get_semantic_hash(program)

    try:
        start_analysis(program_hash)
    except RecursionCycleDetected as e:
        print(f"Debug: {str(e)}", file=sys.stderr)
        return "does not halt"

    try:
        if detect_paradox(program):
            print("Debug: Detected potential halting paradox", file=sys.stderr)
            return "impossible to determine"
        
        static_result = static_preparation(program)
        print(f"Debug: Static result = {static_result}", file=sys.stderr)
        if static_result in ["halts", "does not halt"]:
            return static_result
        
        # --- NEW: Add the heuristic classification phase ---
        heuristic_result = classify_known_problems(program)
        print(f"Debug: Heuristic result = {heuristic_result}", file=sys.stderr)
        if heuristic_result == "impossible to determine":
            return "impossible to determine"

        prover_result = prove_termination(program)
        print(f"Debug: Prover result = {prover_result}", file=sys.stderr)
        if prover_result in ["halts", "does not halt"]:
            return prover_result
        
        dynamic_result = dynamic_tracing(program)
        print(f"Debug: Dynamic result = {dynamic_result}", file=sys.stderr)
        if dynamic_result in ["halts", "does not halt"]:
            return dynamic_result
        
        final_result = decision_synthesis(static_result, prover_result, dynamic_result, program)
        print(f"Debug: Final result = {final_result}", file=sys.stderr)
        return final_result
        
    except Exception as e:
        print(f"Debug: Exception = {str(e)}", file=sys.stderr)
        return f"impossible to determine: {str(e)}"
    finally:
        end_analysis(program_hash)

# The __name__ == "__main__" block contains code that ONLY runs
# when you execute `python main.py` directly.
if __name__ == "__main__":
    # --- NEW: Add command-line argument parsing ---
    parser = argparse.ArgumentParser(
        description="A practical halting analyzer for Python scripts.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--target',
        type=str,
        default=None,
        help="Path to a specific directory of scripts to analyze.\nIf not provided, defaults to the project's 'scripts' directory."
    )
    args = parser.parse_args()

    # Determine which directory to analyze
    if args.target:
        scripts_dir = args.target
        if not os.path.isdir(scripts_dir):
            print(f"Error: Provided target directory does not exist: {scripts_dir}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default behavior
        scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')

    print(f"--- Running Halting Analysis on all scripts in '{scripts_dir}' ---")

    for script_name in sorted(os.listdir(scripts_dir)):
        if script_name.endswith('.py'):
            script_path = os.path.join(scripts_dir, script_name)
            print(f"\n[Analyzing]: {script_name}")
            print("-" * (12 + len(script_name)))
            
            try:
                # Use 'utf-8' encoding for better compatibility
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    program_code = f.read()
                
                result = analyze_halting(program_code)
                print(f"Result: {result}")
                print("-" * (12 + len(script_name)))

            except Exception as e:
                print(f"Error analyzing {script_name}: {e}", file=sys.stderr)
    
    print("\n--- Analysis Complete ---")