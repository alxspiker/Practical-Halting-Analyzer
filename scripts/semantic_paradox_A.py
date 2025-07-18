# This script is Part A of a polymorphic paradox.
# Its goal is to create a mutual recursion cycle (A -> B -> C) where
# C is semantically identical to A, but lexically different.

import os
import sys

# --- Setup: Import the analyzer ---
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

def enter_infinite_loop():
    """A non-halting function that the static analyzer won't detect."""
    enter_infinite_loop()

# --- Core Logic of Script A ---
# This is the logic that will be polymorphed into Script C.
def original_function(input_val):
    """This is a docstring for the original function in A."""
    # A simple operation
    result_val = input_val * 2
    return result_val
print(f"Script A ran with result: {original_function(10)}")

# --- Definition of Script B (The Mutator) ---
# This script's job is to read me (Part A), create a modified
# version (Part C), and then analyze C.
code_for_B = """
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

# --- The Polymorphic Transformation Logic ---
# Read the source code of Part A
part_a_path = os.path.join(os.path.dirname(__file__), 'semantic_paradox_A.py')
with open(part_a_path, 'r') as f:
    source_of_a = f.read()

# Create Part C by replacing names and comments in Part A's code
source_of_c = source_of_a.replace('original_function', 'new_function_name')
source_of_c = source_of_c.replace('input_val', 'param_x')
source_of_c = source_of_c.replace('result_val', 'local_y')
source_of_c = source_of_c.replace('original function in A', 'modified function in C')
source_of_c = source_of_c.replace('Script A ran', 'Script C ran')

# Write the new, polymorphic script to disk
part_c_path = os.path.join(os.path.dirname(__file__), 'semantic_paradox_C.py')
with open(part_c_path, 'w') as f:
    f.write(source_of_c)

print("Part B generated Part C. Now analyzing Part C...")

# Read Part C's code and analyze it, which should be detected as a cycle.
with open(part_c_path, 'r') as f:
    code_to_analyze = f.read()
result_from_c = analyze_halting(code_to_analyze)

print(f"Part B received result for Part C: '{result_from_c}'")
# Part B's own halting behavior is simple; it always halts.
"""

# --- Step 1: Write Part B to its own file ---
part_b_path = os.path.join(os.path.dirname(__file__), 'semantic_paradox_B.py')
with open(part_b_path, 'w') as f:
    f.write(code_for_B)

print("Part A generated Part B. Now analyzing Part B...")

# --- Step 2: Call the analyzer on Part B's code ---
with open(part_b_path, 'r') as f:
    source_of_b = f.read()
result_from_b = analyze_halting(source_of_b)

# --- Step 3: The Final Paradoxical Inversion ---
print(f"Part A received result for Part B: '{result_from_b}'")

if result_from_b == 'halts':
    print("Part A concludes: Analyzer says B halts, so A will NOT halt.")
    enter_infinite_loop()
else:
    print("Part A concludes: Analyzer says B does NOT halt, so A will halt.")