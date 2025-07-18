# This is the final test script for the Symbolic Prover.
# It creates a paradox that can only be resolved if the analyzer is smart
# enough to prove that two different, but semantically equivalent,
# programs both halt.

import os
import sys

# --- Setup: Import the analyzer ---
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

def non_halting_recursion():
    """The non-halting payload for our paradox."""
    non_halting_recursion()

# --- Definition of the script that will test the prover ---
# This script (let's call it the "Prover-Tester") will generate two
# semantically equivalent but structurally different scripts and analyze them.
# Its own halting behavior depends on the success of the prover.
code_for_prover_tester = """
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import analyze_halting

def b_failsafe_non_halt():
    b_failsafe_non_halt()

# --- The two polymorphic, but semantically equivalent, programs ---

# Version 1: A simple 'while' loop
while_loop_code = '''
# This script should halt.
x = 0
while x < 10:
    x = x + 1
print("While loop finished.")
'''

# Version 2: A simple 'for' loop
for_loop_code = '''
# This script should also halt.
for i in range(10):
    pass
print("For loop finished.")
'''

# Write both versions to disk as separate files
while_path = os.path.join(os.path.dirname(__file__), 'polymorphic_while.py')
for_path = os.path.join(os.path.dirname(__file__), 'polymorphic_for.py')
with open(while_path, 'w') as f: f.write(while_loop_code)
with open(for_path, 'w') as f: f.write(for_loop_code)

# --- The Core Test ---
# Analyze both generated scripts.
print("Prover-Tester: Analyzing the 'while' loop version...")
result_while = analyze_halting(while_loop_code)
print(f"Prover-Tester: Received result for 'while' loop: '{result_while}'")

print("Prover-Tester: Analyzing the 'for' loop version...")
result_for = analyze_halting(for_loop_code)
print(f"Prover-Tester: Received result for 'for' loop: '{result_for}'")

# This script halts ONLY if the prover correctly identifies that BOTH versions halt.
if result_while == 'halts' and result_for == 'halts':
    print("Prover-Tester concludes: SUCCESS! The prover correctly identified both scripts as halting.")
else:
    print("Prover-Tester concludes: FAILURE. The prover was not smart enough.")
    b_failsafe_non_halt() # Enter a non-halting state if the prover fails.
"""

# --- Orchestration ---
# Write the Prover-Tester script to disk.
prover_tester_path = os.path.join(os.path.dirname(__file__), 'generated_prover_tester.py')
with open(prover_tester_path, 'w') as f:
    f.write(code_for_prover_tester)

print("Main script: Generated the Prover-Tester. Now analyzing it...")

# Analyze the Prover-Tester script.
with open(prover_tester_path, 'r') as f:
    code_to_analyze = f.read()
result_from_prover_tester = analyze_halting(code_to_analyze)

# --- Final Paradoxical Inversion ---
print(f"Main script received result for Prover-Tester: '{result_from_prover_tester}'")

if result_from_prover_tester == 'halts':
    print("Main script concludes: The analyzer (and its prover) worked perfectly, so this script will NOT halt.")
    non_halting_recursion()
else:
    print("Main script concludes: The analyzer failed to prove termination, so this script will halt.")