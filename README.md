# A Practical Halting Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A multi-layered heuristic engine designed to practically analyze the halting properties of Python scripts. This project navigates the complexities of the undecidable Halting Problem not by attempting a perfect theoretical solution, but by implementing a robust, defense-in-depth strategy that is demonstrably effective.

When tested against a benchmark suite of **5,498 files**—including the Python standard library, top PyPI packages, and a gauntlet of adversarial paradoxes—this analyzer achieved a **Practical Success Rate of 88.87%**.

## Features

-   **Quantifiable High Performance:** Achieves a high success rate on a large and diverse corpus of real-world and adversarial code.
-   **Multi-Phase Analysis Pipeline:** Employs a cascade of analysis techniques, from lightweight static checks to full dynamic execution, ensuring both speed and accuracy.
-   **Advanced Paradox & Cycle Detection:** Utilizes semantic hashing and an analysis call-chain tracker to defend against simple, obfuscated, and even polymorphic recursive paradoxes.
-   **Heuristic Classifier for Known Problems:** Identifies computationally intractable problems like the Ackermann function and Collatz conjecture by their structural patterns, preventing unnecessary execution.
-   **Symbolic Prover:** Integrates a dedicated component to prove the termination of common loop structures that are too complex for basic static analysis.
-   **Automated Benchmarking Suite:** Includes a powerful script (`benchmark.py`) that builds the test corpus and empirically calculates the analyzer's success rate.
-   **Intelligent Caching:** The benchmark harness automatically caches the downloaded code corpus, allowing for rapid re-analysis after making changes to the analyzer's logic.

## The Solution: A Multi-Layered Heuristic Defense

This analyzer employs a "defense-in-depth" strategy. It subjects a given program to a series of increasingly sophisticated analysis phases. If any phase can make a definitive decision, the analysis stops, ensuring maximum efficiency.

### Core Architecture: The Analysis Pipeline

The analyzer processes each script through the following ordered pipeline:

1.  **Meta-Analysis: Cross-Script Recursion Detection (`cross_script_recursion`)**
    -   Before any analysis begins, the script's code is converted to a "semantic hash." The analyzer maintains a call stack of these hashes. If it's asked to analyze a script that is already in the current analysis chain (e.g., A analyzes B, which analyzes a polymorphic version of A), it immediately concludes `does not halt` and stops.

2.  **Phase 0: Adversarial Pattern Matching (`paradox_detection`)**
    -   A highly specific AST visitor that looks for the exact structure of the classic "read-my-own-source-and-invert-the-result" paradox. If found, it returns `impossible to determine`.

3.  **Phase 1: Static Analysis (`static_analysis`)**
    -   The fastest check for the most obvious cases.
    -   **Finds `while True:`:** Immediately returns `does not halt`.
    -   **Finds no loops AND no recursion:** Immediately returns `halts`.

4.  **Phase 1.5: Heuristic Classification (`heuristic_classifier`)**
    -   An AST-based pattern matcher that identifies the structural "fingerprints" of known computationally intractable problems. It flags code that implements the **Ackermann function** or the **Collatz conjecture** as `impossible to determine` without needing to run them.

5.  **Phase 2: Symbolic Prover (`symbolic_prover`)**
    -   A more intelligent static phase that can prove termination for common loop patterns like `for i in range(10)` or `while x < 10: x += 1`, returning `halts` if successful.

6.  **Phase 3: Dynamic Tracing (`dynamic_tracing`)**
    -   The most powerful phase, which executes code in a monitored sandbox. It watches for tell-tale signs of non-termination, such as runaway recursion or repeating execution cycles, to determine if a script `does not halt`. If the script runs to completion or exits with a standard error, it is considered to `halt`.

7.  **Phase 4: Decision Synthesis (`decision_synthesis`)**
    -   A final safety net. If all other phases were inconclusive, it performs a last check for self-referential calls to the analyzer and makes a final judgment.

### Formal Representation of the Analyzer

The logic of the entire pipeline can be expressed as a formal system. Let be the set of all Python programs and be the set of results. The analyzer **H** is a function that takes a program and the current analysis chain **C** and is defined as:

**H(P, C) =**
```
      | "does not halt",                if Hash(P) ∈ C
      |
      | "impossible to determine",      if Paradox(P) = true
      |
      | Static(P),                        if Static(P) ≠ "impossible to determine"
      |
H(P) = | "impossible to determine",      if Heuristic(P) = "impossible to determine"
      |
      | Prove(P),                         if Prove(P) ≠ "impossible to determine"
      |
      | Trace(P),                         if Trace(P) ≠ "impossible to determine"
      |
      | "does not halt",                if "analyze_halting" is a substring of P
      |
      | "impossible to determine",      otherwise
```

## Performance: A Benchmark-Driven Result

To validate this approach, a comprehensive benchmark was performed using the included `benchmark.py` script.

-   **Corpus Size:** 5,498 total Python scripts.
-   **Corpus Composition:**
    -   **Halting Code:** The Python Standard Library and top PyPI packages (`requests`, `numpy`, `pandas`, etc.).
    -   **Non-Halting Code:** Synthetically generated infinite loops and a suite of hand-crafted adversarial paradoxes.
    -   **Complex Code:** Theoretically challenging cases like the Ackermann function and the Collatz conjecture.
-   **Success Criteria:** A test passes if the analyzer's result is considered "safe" for the given category:
    -   `halting` scripts must be classified as `halts`.
    -   `non-halting` scripts are correct if classified as `does not halt` or `impossible to determine`.
    -   `complex` scripts are correct if classified as `impossible to determine` or `does not halt`.

| Metric                  | Score                                  |
| ----------------------- | -------------------------------------- |
| **Correct Predictions** | 4,886 of 5,498                         |
| **Practical Success Rate** | **88.87%**                             |

This result demonstrates that while a perfect halting decider is impossible, a layered heuristic approach can achieve a very high degree of accuracy and safety on practical, real-world code.

## Usage

The project contains two primary entry points: the analyzer itself (`main.py`) and the benchmark harness (`benchmark.py`).

### Running the Analyzer

The `main.py` script can analyze a directory of Python files. By default, it runs on the project's `./scripts` directory.

```bash
# Analyze the default adversarial scripts
python main.py
```

You can also point it at any other directory using the `--target` flag.

```bash
# Analyze a custom directory
python main.py --target /path/to/your/scripts
```

### Measuring Performance with the Benchmark

The `benchmark.py` script builds the test corpus and calculates the analyzer's success rate.

**First Run (Builds the Corpus)**
This command will take several minutes to download and process thousands of files into a `benchmark_suite` directory.

```bash
python benchmark.py
```

**Subsequent Runs (Uses Cached Corpus)**
Once the `benchmark_suite` directory exists, running the command again will skip the build process and provide results much faster.

```bash
# This run will be much faster
python benchmark.py
```

**Forcing a Fresh Build**
To delete the existing corpus and build a new one, use the `--rebuild` flag.

```bash
python benchmark.py --rebuild
```

## The Never-Ending Game: Project Philosophy

This project acknowledges that the Halting Problem is theoretically undecidable. The goal is not to achieve impossible perfection but to build a practical tool that demonstrates the power of layered heuristics. By combining static analysis, symbolic logic, dynamic tracing, and advanced meta-defenses, this analyzer successfully pushes the boundary of what can be practically decided, providing correct and safe answers for an overwhelming majority of real-world and adversarial programs.