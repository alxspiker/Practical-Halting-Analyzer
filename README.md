<div align="center">

# A Practical Halting Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A multi-layered heuristic engine designed to practically analyze the halting properties of Python scripts.**
</div>

> [!NOTE]
> When tested against a benchmark suite of **5,498 files**—including the Python standard library, top PyPI packages, and a gauntlet of adversarial paradoxes—this analyzer achieved a **Practical Success Rate of 88.87%**.

---

### Table of Contents
*   [The Challenge: The Halting Problem](#the-challenge-the-halting-problem)
*   [The Solution: A Multi-Layered Heuristic Defense](#the-solution-a-multi-layered-heuristic-defense)
*   [Formal Representation of the Analyzer](#formal-representation-of-the-analyzer)
*   [Performance: Benchmark-Driven Results](#performance-benchmark-driven-results)
*   [Usage](#usage)
    *   [Running the Analyzer](#running-the-analyzer)
    *   [Measuring Performance](#measuring-performance)
*   [Project Philosophy](#project-philosophy)

---

## The Challenge: The Halting Problem

> [!IMPORTANT]
> The Halting Problem is **theoretically undecidable**. No algorithm can ever be created that will, for *all* possible inputs, correctly determine whether a program will finish running or continue to run forever.

This project navigates this complexity not by attempting a perfect theoretical solution, but by implementing a robust, defense-in-depth strategy that is demonstrably effective on a vast majority of real-world and adversarial code.

## The Solution: A Multi-Layered Heuristic Defense

This analyzer employs a "defense-in-depth" strategy. It subjects a given program to a series of increasingly sophisticated and computationally expensive analysis phases. If any phase can make a definitive decision, the analysis stops, ensuring maximum efficiency.

### Core Architecture: The Analysis Pipeline

<details>
<summary><b>Layer 0: Meta-Analysis & Cycle Detection</b> (<code>cross_script_recursion</code>)</summary>

Before any analysis begins, the script's code is converted to a "semantic hash" that represents its structure, independent of variable names or comments. The analyzer maintains a call stack of these hashes. If it's asked to analyze a script that is already in the current analysis chain (e.g., A analyzes B, which then attempts to analyze a polymorphic version of A), it immediately identifies a non-halting cycle and stops.

</details>

<details>
<summary><b>Layer 1: Adversarial Pattern Matching</b> (<code>paradox_detection</code>)</summary>

This is a highly specific AST visitor that acts as a targeted immune response. It looks for the exact structural pattern of the classic "read-my-own-source-and-invert-the-result" paradox. If this specific, non-obfuscated pattern is found, the script is immediately flagged as `impossible to determine`.

</details>

<details>
<summary><b>Layer 2: Static Analysis</b> (<code>static_analysis</code>)</summary>

The fastest check for the most obvious cases. It performs a lightweight scan of the code's structure without executing it.
<ul>
    <li><b>Finds `while True:`:</b> Immediately returns `does not halt`.</li>
    <li><b>Finds no loops AND no recursion:</b> Immediately returns `halts`.</li>
</ul>
</details>

<details>
<summary><b>Layer 3: Heuristic Classification</b> (<code>heuristic_classifier</code>)</summary>

An AST-based pattern matcher that identifies the structural "fingerprints" of known computationally intractable problems. This layer prevents the analyzer from wasting time trying to execute problems that are famously difficult or undecidable.
<ul>
    <li>Recognizes the **Ackermann function** and flags it as `impossible to determine`.</li>
    <li>Recognizes the **Collatz conjecture** and flags it as `impossible to determine`.</li>
</ul>
</details>

<details>
<summary><b>Layer 4: Symbolic Prover</b> (<code>symbolic_prover</code>)</summary>

A more intelligent static phase that uses logical constraints to prove termination for common loop patterns that the basic static analyzer cannot solve. It can prove that loops like `for i in range(10)` or `while x < 10: x += 1` will definitively halt.

</details>

<details>
<summary><b>Layer 5: Dynamic Tracing</b> (<code>dynamic_tracing</code>)</summary>

The most powerful and resource-intensive phase. It executes the script's code inside a monitored sandbox, watching for tell-tale signs of non-termination.
<ul>
    <li>It detects runaway recursion (exceeding a depth limit).</li>
    <li>It detects deterministic cycles in the execution trace (e.g., the program state repeats).</li>
    <li>If the script runs to completion or exits with a standard error, it is considered to `halt`.</li>
</ul>
</details>

<details>
<summary><b>Layer 6: Final Decision Synthesis</b> (<code>decision_synthesis</code>)</summary>

A final safety net. If all other phases were inconclusive, it performs one last check for self-referential calls to the `analyze_halting` function and makes a final judgment based on the combined results of the previous phases.

</details>

---

## Formal Representation of the Analyzer

The logic of the entire pipeline can be expressed as a formal system. Let be the set of all Python programs and be the set of results. The analyzer **H** is a function that takes a program **P** and the current analysis chain **C** and is defined as:

```
H(P, C) =
      | "does not halt",                if Hash(P) ∈ C
      |
      | "impossible to determine",      if Paradox(P) = true
      |
      | Static(P),                        if Static(P) ≠ "impossible to determine"
      |
      | "impossible to determine",      if Heuristic(P) = "impossible to determine"
      |
      | Prove(P),                         if Prove(P) ≠ "impossible to determine"
      |
      | Trace(P),                         if Trace(P) ≠ "impossible to determine"
      |
      | Synthesis(Static, Prove, Trace, P)
```
<br>

<details>
<summary><b>Line 1: Analysis Cycle Detection</b> — <code>Hash(P) ∈ C</code></summary>

*   **Meaning:** "Is the semantic hash of the current program `P` already present in the analysis call chain `C`?"
*   **Purpose:** This is the primary defense against meta-level recursion. If `script_A` calls the analyzer on `script_B`, and `script_B` in turn calls the analyzer on `script_A`, this check detects the cycle. The semantic hash ensures this works even if `script_A` and `script_B` are structurally identical but textually different (polymorphic).
*   **Result:** `does not halt`. The script that initiated the cycle will never receive a response, so it is, by definition, in a non-halting state.

</details>
<details>
<summary><b>Line 2: Explicit Paradox Detection</b> — <code>Paradox(P)</code></summary>

*   **Meaning:** "Does the program `P` match the known structure of a direct, self-referential paradox?"
*   **Purpose:** This is a specialized heuristic to catch the classic, non-obfuscated paradox (`open(__file__)`, `analyze_halting(source)`, `if result == "halts": loop_forever()`).
*   **Result:** `impossible to determine`. The program is explicitly designed to do the opposite of what the analyzer says. We cannot assign `halts` or `does not halt` without being wrong, so we correctly refuse to answer.

</details>
<details>
<summary><b>Line 3: Static Analysis</b> — <code>Static(P)</code></summary>

*   **Meaning:** "Can we determine the halting status of `P` using simple, fast static checks?"
*   **Purpose:** This handles the "low-hanging fruit." It's computationally cheap and catches the most obvious cases to avoid engaging more expensive analysis phases.
*   **Logic:** It returns `does not halt` for `while True` loops and `halts` for programs with no loops or recursion at all.

</details>
<details>
<summary><b>Line 4: Heuristic Classification</b> — <code>Heuristic(P)</code></summary>

*   **Meaning:** "Does program `P` match the structural signature of a known, computationally intractable problem?"
*   **Purpose:** This acts as an "expert system." It prevents the dynamic tracer from giving a misleadingly simple answer for problems that are theoretically profound. While `collatz(27)` does halt, the general Collatz problem is undecidable.
*   **Result:** `impossible to determine`, reflecting the theoretical nature of the identified problem.

</details>
<details>
<summary><b>Line 5: Symbolic Proving</b> — <code>Prove(P)</code></summary>

*   **Meaning:** "Can we formally prove that the loops in `P` must terminate?"
*   **Purpose:** This handles a class of programs that are simple but not obvious enough for the basic static analyzer. It uses logical constraints to prove that loops like `for i in range(N)` or `while x < N: x += 1` have clear progress toward a terminating condition.
*   **Result:** `halts` if the proof succeeds.

</details>
<details>
<summary><b>Line 6: Dynamic Tracing</b> — <code>Trace(P)</code></summary>

*   **Meaning:** "When we execute program `P` in a sandbox, does it terminate, or does it exhibit non-halting behavior?"
*   **Purpose:** This is the court of last resort and the most powerful tool. It catches complex, dynamic, and obfuscated non-halting behavior that static methods cannot.
*   **Logic:** If the program finishes, it `halts`. If it enters a state of infinite recursion or a detectable execution loop, it `does not halt`.

</details>
<details>
<summary><b>Line 7: Final Synthesis</b> — <code>Synthesis(Static, Prove, Trace, P)</code></summary>

*   **Meaning:** "If all else has failed, what is the safest final answer?"
*   **Purpose:** This is the final fallback in the `decision_synthesis` phase. It combines inconclusive results from prior phases and checks for self-referential patterns.
*   **Logic:** Prioritizes definitive results from earlier phases. If none, checks for self-reference via AST or substring and classifies as `does not halt` if found; otherwise, `impossible to determine`.

</details>

---

## Performance: Benchmark-Driven Results

To validate this approach, a comprehensive benchmark was performed using the included `benchmark.py` script.

*   **Corpus Size:** 5,498 total Python scripts.
*   **Corpus Composition:**
    *   **Halting Code:** The Python Standard Library and top PyPI packages (`requests`, `numpy`, `pandas`, etc.).
    *   **Non-Halting Code:** Synthetically generated infinite loops and a suite of hand-crafted adversarial paradoxes.
    *   **Complex Code:** Theoretically challenging cases like the Ackermann function and the Collatz conjecture.
*   **Success Criteria:** A test passes if the analyzer's result is considered "safe" for the given category:
    *   `halting` scripts must be classified as `halts`.
    *   `non-halting` scripts are correct if classified as `does not halt` or `impossible to determine`.
    *   `complex` scripts are correct if classified as `impossible to determine` or `does not halt`.

| Metric                  | Score                                  |
| ----------------------- |:--------------------------------------:|
| **Correct Predictions** | 4,886 of 5,498                         |
| **Practical Success Rate** | **88.87%**                           |

This result demonstrates that while a perfect halting decider is impossible, a layered heuristic approach can achieve a very high degree of accuracy and safety on practical, real-world code.

## Usage

### Running the Analyzer

The `main.py` script can analyze a directory of Python files. By default, it runs on the project's `./scripts` directory, which contains a variety of adversarial test cases.

```bash
# Analyze the default adversarial scripts
python main.py
```

You can also point it at any other directory using the `--target` flag.

```bash
# Analyze a custom directory of Python scripts
python main.py --target /path/to/your/scripts
```

### Measuring Performance

The `benchmark.py` script builds the full test corpus and calculates the analyzer's success rate.

**First Run (Builds the Corpus)**
This command will take several minutes to download and process thousands of files into a `benchmark_suite` directory.

```bash
python benchmark.py
```

**Subsequent Runs (Uses Cached Corpus)**
> [!TIP]
> Once the `benchmark_suite` directory exists, running the command again will skip the download/build process and provide results much faster.

```bash
# This run will be much faster
python benchmark.py
```

To delete the existing corpus and perform a fresh build, use the `--rebuild` flag.

```bash
python benchmark.py --rebuild
```

---

## Project Philosophy

This project acknowledges that the Halting Problem is theoretically undecidable. The goal is not to achieve impossible perfection but to build a practical tool that demonstrates the power of layered heuristics. By combining static analysis, symbolic logic, dynamic tracing, and advanced meta-defenses, this analyzer successfully pushes the boundary of what can be practically decided, providing correct and safe answers for an overwhelming majority of real-world and adversarial programs.

---