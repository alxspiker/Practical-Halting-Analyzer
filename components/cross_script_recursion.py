# A new data structure to track the analysis call chain.
# Using a list allows us to see the entire path, e.g., [A, B, C]
# which represents "A is analyzing B, which is analyzing C".
_analysis_chain = []

class RecursionCycleDetected(Exception):
    """Custom exception for clear error handling."""
    pass

def start_analysis(program_hash: str):
    """
    Adds a program to the analysis chain.
    Raises RecursionCycleDetected if the program is already in the chain.
    """
    if program_hash in _analysis_chain:
        # A cycle is detected!
        cycle_path = " -> ".join(_analysis_chain) + f" -> {program_hash}"
        raise RecursionCycleDetected(f"Mutual recursion detected in analysis chain: {cycle_path}")
    
    _analysis_chain.append(program_hash)

def end_analysis(program_hash: str):
    """
    Removes a program from the end of the analysis chain.
    Raises an exception if the chain is corrupt (this shouldn't happen).
    """
    if not _analysis_chain or _analysis_chain[-1] != program_hash:
        # This indicates a bug in the analyzer's logic.
        raise RuntimeError("Analysis chain is corrupted. Mismatched end_analysis call.")
    
    _analysis_chain.pop()