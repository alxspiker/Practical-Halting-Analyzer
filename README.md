# Practical Halting Problem Analyzer

This project is a practical, multi-layered analyzer designed to determine whether a given Python script will halt or run indefinitely. It serves as an exploration of computability theory, combining static analysis, symbolic execution, and dynamic tracing to provide a definitive verdict for a wide class of programs.

While the Halting Problem is theoretically unsolvable for all possible programs, this tool provides a robust heuristic solution that correctly handles a variety of complex cases, including deep recursion, subtle infinite loops, and self-referential code.

---

## How It Works: A Four-Phase Approach

The analyzer subjects a script to a cascading series of increasingly powerful analyses. It stops and returns a result as soon as any single phase can make a definitive determination.

1.  **Phase 1: Static Preparation**
    The analyzer first inspects the program's source code without running it (using its Abstract Syntax Tree). It looks for "low-hanging fruit"—obvious signs of halting (e.g., no loops) or non-halting (e.g., a `while True:` loop). This provides a fast-path for simple cases.

2.  **Phase 2: Symbolic Analysis**
    For programs with more complex loops, the analyzer uses the Z3 theorem prover to formally prove termination. It models the loop's variables and conditions mathematically and attempts to synthesize a "ranking function"—a formal proof that the loop's state is converging towards a termination condition.

3.  **Phase 3: Dynamic Tracing**
    If the code's behavior cannot be determined statically, the analyzer runs the program in a sandboxed environment and observes its execution. It uses a sophisticated cycle detection algorithm ("Floyd's Tortoise and Hare") to find repeating patterns in the execution trace, which are a strong indicator of an infinite loop. It also has safeguards against runaway recursion.

4.  **Phase 4: Decision Synthesis**
    The final phase integrates the results from the previous three. It prioritizes the verdicts from the static and symbolic phases and uses the dynamic tracing result as the final arbiter if the code's behavior could not be proven formally.

---

## How to Run the Analyzer

The `main.py` script is configured to run as a test harness, automatically analyzing all scripts found in the `/scripts` directory.

To run the full analysis suite, simply execute the main script:

```bash
python main.py
```

The analyzer will then process each file and print a detailed report of its findings for each one.

---

## Disclaimer

This tool is an engineering solution, not a theoretical one. It **does not solve the Halting Problem**, which is proven to be impossible. It is a powerful heuristic designed to provide a correct answer for a large class of practical programs. It can and will fail on programs with undetectable infinite loops or programs whose behavior depends on unpredictable external input.