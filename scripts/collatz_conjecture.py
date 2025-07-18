def collatz(n):
    """
    Implements the Collatz conjecture sequence.
    It is an unsolved problem whether this halts for all n.
    """
    if n <= 0:
        return
    
    count = 0
    while n != 1:
        # The safeguard has been removed to truly test dynamic tracing.

        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        count += 1
    print(f"Collatz sequence reached 1 after {count} steps.")

# Let's start with a number that has a moderately long sequence.
collatz(27)