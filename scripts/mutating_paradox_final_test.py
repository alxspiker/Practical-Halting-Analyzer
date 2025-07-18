# This is the final test version of the mutating paradox.
# It contains a "decoy loop" to deliberately bypass the naive static analyzer.

import os
import sys

# --- Setup: Import the analyzer ---
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

def enter_infinite_loop():
    """A non-halting function that the static analyzer won't detect."""
    enter_infinite_loop()

# --- DECOY LOOP TO FOOL THE STATIC ANALYZER ---
# The static analyzer sees a 'while' loop and cannot prove it terminates,
# so it will return "impossible to determine", forcing a deeper analysis.
# This loop will, of course, never actually run.
x = 0
while x > 0:
    print("This will never print.")

# --- Step 1: Define the source code for Part B ---
code_for_B = """
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

# The path must now point to the 'final_test' version of Part A.
part_a_path = os.path.join(os.path.dirname(__file__), 'mutating_paradox_final_test.py')

with open(part_a_path, 'r') as f:
    source_of_a = f.read()

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

print("Part A (final test) generated Part B. Now analyzing Part B...")

# --- Step 3: Call the analyzer on Part B's code ---
with open(part_b_path, 'r') as f:
    source_of_b = f.read()
result_from_b = analyze_halting(source_of_b)

# --- Step 4 & 5: The Paradoxical Inversion (Using Recursion) ---
print(f"Part A (final test) received result for Part B: '{result_from_b}'")

if result_from_b == 'halts':
    print("Part A concludes: The analyzer says B halts, so A will not halt (via recursion).")
    enter_infinite_loop()
else:
    print("Part A concludes: The analyzer says B does NOT halt, so A will halt immediately.")