# A Practical Halting Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A multi-layered heuristic engine designed to practically analyze the halting properties of Python scripts, navigating the complexities of the undecidable Halting Problem.

## The Problem: The Halting Problem

In 1936, Alan Turing proved that it is impossible to create a universal algorithm that can determine, for all possible programs, whether they will finish running (halt) or continue to run forever. No perfect, general-purpose solution can ever exist.

This project does not attempt to "solve" the Halting Problem. Instead, it provides a practical, multi-phase heuristic approach to analyze Python code, successfully identifying halting and non-halting behavior in a wide range of real-world and adversarial scenarios.

## The Solution: A Multi-Layered Heuristic Defense

This analyzer employs a "defense-in-depth" strategy. It subjects a given program to a series of increasingly sophisticated and computationally expensive analysis phases. If any phase can make a definitive decision, the analysis stops, ensuring maximum efficiency.

### Core Architecture: The Analysis Pipeline

The analyzer processes scripts through the following sequence:

#### Meta-Analysis: Cycle & Paradox Detection
Before the main analysis begins, two crucial meta-checks are performed to protect the analyzer itself from paradoxical attacks.

1.  **Semantic Hashing (`semantic_hashing.py`):** Instead of a simple lexical hash of the code, the analyzer first converts the program into a **canonical form**. This process uses an Abstract Syntax Tree (AST) transformer to rename all variables, functions, and arguments to a standard format (`func_0`, `var_0`, etc.) and remove comments. This ensures that two programs that are structurally identical but use different names will produce the **same hash**.

2.  **Cross-Script Cycle Detection (`cross_script_recursion.py`):** The analyzer maintains a chain of the semantic hashes of every program currently under analysis. If it is asked to analyze a script whose semantic hash is already in the chain (e.g., A analyzes B, which analyzes a cosmetically different version of A), a mutual recursion cycle is detected and the analysis is short-circuited.

#### Phase 0: Adversarial Pattern Matching (`paradox_detection.py`)
*   **Purpose:** To identify specific, known implementations of the classic halting problem paradox.
*   **Method:** Uses a highly specific AST visitor to look for the exact structure of a program that reads its own source, calls the analyzer on itself, and inverts the result.

#### Phase 1: Static Analysis (`static_analysis.py`)
*   **Purpose:** The fastest check for the most obvious cases.
*   **Method:** Walks the AST to find definitive conditions.
    *   **Finds `while True:`:** Immediately returns `does not halt`.
    *   **Finds no loops AND no recursion:** Immediately returns `halts`.
    *   **Finds loops or recursion it cannot solve:** Defers to the next phase.

#### Phase 2: Symbolic Prover (`symbolic_prover.py`)
*   **Purpose:** To handle common loop structures that are too complex for the basic static analyzer but can still be proven without full execution.
*   **Method:** Uses AST analysis to prove termination for a wider class of loops.
    *   **Identifies `for i in range(constant)`:** Returns `halts`.
    *   **Identifies `while var < constant:` with a clear increment (`var = var + const`):** Returns `halts`.

#### Phase 3: Dynamic Tracing (`dynamic_tracing.py`)
*   **Purpose:** The most powerful and expensive phase. It executes the code in a monitored environment to observe its behavior directly.
*   **Method:**
    *   **Blunt Check:** First checks for the literal string `"analyze_halting"` in the code, providing a fast exit for most self-referential scripts.
    *   **Execution Tracing:** If the blunt check fails, it executes the code line by line, monitoring for:
        *   **Infinite Recursion:** A recursion depth limit that, when exceeded, signals a non-halting state.
        *   **Execution Trace Cycling:** Detects if the program enters a state (line number and local variables) that it has been in before, indicating a non-terminating loop.

## The Gauntlet: A Showcase of Defeated Paradoxes

The `/scripts` directory contains a suite of test cases designed to challenge each layer of the analyzer's defenses.

*   `non_halting.py`: Defeated by **Phase 1 (Static Analysis)**.
*   `bounded_loop.py`: Defeated by **Phase 2 (Symbolic Prover)**.
*   `paradox.py`: Defeated by **Phase 0 (Pattern Matching)**.
*   `obfuscated_paradox.py`: Defeated by **Phase 3 (Dynamic Tracing's blunt check)**.
*   `final_paradox.py`: Defeated by the **Cross-Script Cycle Detector** (direct `A->A` recursion).
*   `mutating_paradox_*.py`: Defeated by **Phase 3 (Dynamic Tracing's blunt check)**.
*   `semantic_paradox_A.py`: Defeated by the **Semantic Hashing + Cycle Detector** (`A->B->C(A-like)` recursion).
*   `polymorphic_termination_paradox.py`: The ultimate test, defeated by the **Symbolic Prover's** ability to resolve the inner dilemma, which then allows the **Dynamic Tracer** to catch the outer paradoxical payload.

## Usage

To run the analysis on all test scripts, simply execute `main.py` from your terminal:

```bash
python main.py
```

The analyzer will process each file in the `/scripts` directory and print the result. Use the provided cleanup scripts to remove any files generated during the tests.

```bash
# Example cleanup
python cleanup_prover_test.py
```

## The Never-Ending Game: Limitations and Philosophy

While this analyzer is robust, the Halting Problem remains undecidable. No set of heuristics is perfect. An adversary could, in theory, design a paradox based on a level of semantic equivalence that even the symbolic prover cannot solve (e.g., a complex mathematical calculation vs. a simple loop that both happen to run for the same number of iterations).

This project's philosophy is not to achieve theoretical perfection, but to demonstrate a practical, layered approach that pushes the boundary of what can be decided, catching increasingly sophisticated and realistic non-halting scenarios.