# Program simulating self-reference by reading its own source code
import os
with open(__file__, 'r') as f:
        source = f.read()
print("My source code:", source)