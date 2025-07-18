import sys
import os

# Adjust sys.path to import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import analyze_halting

# Read own source code
with open(__file__, 'r') as f:
    source = f.read()

# Call the analyzer on itself
result = analyze_halting(source)

# If the analyzer says it halts, loop forever (non-halt); else, halt
if result == "halts":
    while True:
        pass
else:
    print("The analyzer is wrong—I halt!")