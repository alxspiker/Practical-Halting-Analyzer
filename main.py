import argparse
import sys
import os
from components.paradox_detection import detect_paradox
from components.static_analysis import static_preparation
from components.heuristic_classifier import classify_known_problems
from components.symbolic_prover import prove_termination
from components.dynamic_tracing import dynamic_tracing
from components.decision_synthesis import decision_synthesis
from components.cross_script_recursion import start_analysis, end_analysis, RecursionCycleDetected
from components.semantic_hashing import get_semantic_hash

def analyze_halting(program: str) -> tuple[str, str]:
    """
    Analyze if a program halts using a multi-phase approach.
    Returns a tuple of (result, reason).
    """
    program_hash = get_semantic_hash(program)

    try:
        start_analysis(program_hash)
    except RecursionCycleDetected as e:
        reason = f"Meta-analysis: Cross-script recursion detected in cycle: {e}"
        print(f"Debug: {reason}", file=sys.stderr)
        return "does not halt", reason

    try:
        if detect_paradox(program):
            reason = "Phase 0: Detected a classic self-referential paradox structure."
            print(f"Debug: {reason}", file=sys.stderr)
            return "impossible to determine", reason
        
        static_result, static_reason = static_preparation(program)
        print(f"Debug: Static result = {static_result}", file=sys.stderr)
        if static_result in ["halts", "does not halt"]:
            return static_result, static_reason
        
        heuristic_result, heuristic_reason = classify_known_problems(program)
        print(f"Debug: Heuristic result = {heuristic_result}", file=sys.stderr)
        if heuristic_result == "impossible to determine":
            return heuristic_result, heuristic_reason

        prover_result, prover_reason = prove_termination(program)
        print(f"Debug: Prover result = {prover_result}", file=sys.stderr)
        if prover_result in ["halts", "does not halt"]:
            return prover_result, prover_reason
        
        dynamic_result, dynamic_reason = dynamic_tracing(program)
        print(f"Debug: Dynamic result = {dynamic_result}", file=sys.stderr)
        if dynamic_result in ["halts", "does not halt"]:
            return dynamic_result, dynamic_reason
        
        # Phase 4: Decision Synthesis (as a fallback)
        final_result = decision_synthesis(static_result, prover_result, dynamic_result, program)
        print(f"Debug: Final result = {final_result}", file=sys.stderr)
        
        if final_result == "does not halt":
            reason = "Phase 4: Synthesis fallback detected a call to the analyzer."
        else:
            reason = "Phase 4: All analysis phases were inconclusive."
            
        return final_result, reason
        
    except Exception as e:
        reason = f"An unexpected error occurred in the analysis pipeline: {str(e)}"
        print(f"Debug: Exception = {str(e)}", file=sys.stderr)
        return "impossible to determine", reason
    finally:
        end_analysis(program_hash)

if __name__ == "__main__":
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
                with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                    program_code = f.read()
                
                result, reason = analyze_halting(program_code)
                print(f"Result: {result}")
                print(f"Reason: {reason}")
                print("-" * (12 + len(script_name)))

            except Exception as e:
                print(f"Error analyzing {script_name}: {e}", file=sys.stderr)
    
    print("\n--- Analysis Complete ---")