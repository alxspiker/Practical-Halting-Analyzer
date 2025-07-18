def ackermann(m, n):
    if m == 0:
        return n + 1
    elif m > 0 and n == 0:
        return ackermann(m - 1, 1)
    elif m > 0 and n > 0:
        return ackermann(m - 1, ackermann(m, n - 1))
    return None

# This will halt, but only after an immense number of steps.
# It is a severe test for the recursion depth and timeout handling.
print(ackermann(2, 2))