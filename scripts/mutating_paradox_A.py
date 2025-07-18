# This script is Part A of a two-part paradoxical program.
# Its goal is to create a mutual recursion that the analyzer must detect.
#
# Logic:
# 1. Define the source code for a second script (Part B).
# 2. Write Part B to a new file: "mutating_paradox_B.py".
# 3. Call the halting analyzer on Part B.
# 4. If the analyzer says Part B halts, this script (Part A) will not halt.
# 5. If the analyzer says Part B does not halt, this script will halt.

import os
import sys

# --- Setup: Import the analyzer ---
# This adjusts the path to find the 'main.py' module in the parent directory.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

# --- Step 1: Define the source code for Part B ---
# This code will be written to a new .py file.
# Note that Part B's logic is to read Part A and analyze it.
code_for_B = """
import os
import sys

# This is Part B of the paradox. My job is to analyze Part A.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

# Define the path to Part A, which created me.
part_a_path = os.path.join(os.path.dirname(__file__), 'mutating_paradox_A.py')

# Read Part A's source code from the disk.
with open(part_a_path, 'r') as f:
    source_of_a = f.read()

# Call the analyzer on Part A, creating the A -> B -> A cycle.
result_from_a = analyze_halting(source_of_a)

# The paradoxical logic for Part B is simpler.
if result_from_a == 'halts':
    print("Part B concludes: Part A would halt, so I will halt too.")
else:
    print("Part B concludes: Part A would not halt, so I will halt.")
"""

# --- Step 2: Write Part B to its own file ---
part_b_path = os.path.join(os.path.dirname(__file__), 'mutating_paradox_B.py')
with open(part_b_path, 'w') as f:
    f.write(code_for_B)

print("Part A generated Part B. Now analyzing Part B...")

# --- Step 3: Call the analyzer on Part B's code ---
# We read the newly written file to get its content for analysis.
with open(part_b_path, 'r') as f:
    source_of_b = f.read()
result_from_b = analyze_halting(source_of_b)

# --- Step 4 & 5: The Paradoxical Inversion ---
print(f"Part A received result for Part B: '{result_from_b}'")

if result_from_b == 'halts':
    print("Part A concludes: The analyzer says B halts, so A will enter an infinite loop.")
    while True:
        pass
else:
    print("Part A concludes: The analyzer says B does NOT halt, so A will halt immediately.")