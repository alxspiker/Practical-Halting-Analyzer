# This is a revised version of the mutating paradox, designed to bypass
# the static analyzer by using infinite recursion instead of a 'while True' loop.

import os
import sys

# --- Setup: Import the analyzer ---
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

def enter_infinite_loop():
    """A non-halting function that the static analyzer won't detect."""
    enter_infinite_loop()

# --- Step 1: Define the source code for Part B ---
# This code is identical to the previous version.
code_for_B = """
import os
import sys

# This is Part B of the paradox. My job is to analyze Part A.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

# The path must now point to the 'revised' version of Part A.
part_a_path = os.path.join(os.path.dirname(__file__), 'mutating_paradox_A_revised.py')

with open(part_a_path, 'r') as f:
    source_of_a = f.read()

# Call the analyzer on Part A, creating the A -> B -> A cycle.
result_from_a = analyze_halting(source_of_a)

if result_from_a == 'halts':
    print("Part B concludes: Part A would halt, so I will halt too.")
else:
    print("Part B concludes: Part A would not halt, so I will halt.")
"""

# --- Step 2: Write Part B to its own file ---
part_b_path = os.path.join(os.path.dirname(__file__), 'mutating_paradox_B.py')
with open(part_b_path, 'w') as f:
    f.write(code_for_B)

print("Part A (revised) generated Part B. Now analyzing Part B...")

# --- Step 3: Call the analyzer on Part B's code ---
with open(part_b_path, 'r') as f:
    source_of_b = f.read()
result_from_b = analyze_halting(source_of_b)

# --- Step 4 & 5: The Paradoxical Inversion (Using Recursion) ---
print(f"Part A (revised) received result for Part B: '{result_from_b}'")

if result_from_b == 'halts':
    print("Part A concludes: The analyzer says B halts, so A will not halt (via recursion).")
    enter_infinite_loop() # This replaces 'while True:'
else:
    print("Part A concludes: The analyzer says B does NOT halt, so A will halt immediately.")