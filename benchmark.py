import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
import sys
import argparse
import multiprocessing
import time

from main import analyze_halting

# --- Configuration ---
BENCHMARK_DIR = Path("benchmark_suite")
HALTING_DIR = BENCHMARK_DIR / "halting"
NON_HALTING_DIR = BENCHMARK_DIR / "non-halting"
COMPLEX_DIR = BENCHMARK_DIR / "complex"

STDLIB_DEST = HALTING_DIR / "stdlib"
PYPI_DEST = HALTING_DIR / "pypi_sources"
SYNTHETIC_DEST = NON_HALTING_DIR / "synthetic"
PARADOXES_DEST = NON_HALTING_DIR / "paradoxes"

PYPI_PACKAGES = [
    "requests", "numpy", "pandas", "flask", "django",
    "scikit-learn", "matplotlib", "beautifulsoup4", "sqlalchemy", "celery"
]
NUM_SYNTHETIC = 50
NON_HALTING_PATTERNS = [
    ("while_true", "while True:\n    pass"),
    ("unbounded_inc", "x = 0\nwhile x >= 0:\n    x += 1"),
    ("unbounded_dec", "x = 0\nwhile x <= 0:\n    x -= 1"),
    ("simple_recursion", "def f():\n    f()\nf()"),
    ("mutual_recursion", "def f():\n    g()\ndef g():\n    f()\nf()"),
]
PROJECT_SCRIPTS_DIR = Path("scripts")

# --- Helper Functions for Corpus Creation ---

def create_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def collect_stdlib():
    create_directory(STDLIB_DEST)
    stdlib_path = Path(shutil.__file__).parent
    print(f"Collecting files from stdlib at: {stdlib_path}")
    file_count = 0
    for root, _, files in os.walk(stdlib_path):
        for file in files:
            if file.endswith(".py"):
                try:
                    shutil.copy(Path(root) / file, STDLIB_DEST)
                    file_count += 1
                except Exception: pass
    print(f"Copied {file_count} stdlib files.")

def download_and_unpack_pypi():
    create_directory(PYPI_DEST)
    print("Downloading PyPI packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "--dest", str(PYPI_DEST), *PYPI_PACKAGES], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"pip download failed: {e.stderr.decode()}. Skipping.")
        return
    unpacked_dir = PYPI_DEST / "unpacked"
    create_directory(unpacked_dir)
    archives_to_delete = []
    print("Unpacking archives...")
    for archive in PYPI_DEST.iterdir():
        if archive.is_file():
            try:
                if archive.suffix in (".tar.gz", ".tgz"):
                    with tarfile.open(archive, "r:gz") as tar: tar.extractall(path=unpacked_dir)
                elif archive.suffix == ".whl":
                    with zipfile.ZipFile(archive, "r") as zip_ref: zip_ref.extractall(path=unpacked_dir)
                archives_to_delete.append(archive)
            except Exception as e:
                print(f"Warning: Could not unpack {archive.name}: {e}")
    file_count = 0
    print("Collecting .py files from packages...")
    for root, _, files in os.walk(unpacked_dir):
        for file in files:
            if file.endswith(".py"):
                source_path = Path(root) / file
                unique_name = f"{source_path.parent.name.replace('-', '_')}_{source_path.name}"
                if not (PYPI_DEST / unique_name).exists():
                    shutil.copy(source_path, PYPI_DEST / unique_name)
                    file_count += 1
    print("Cleaning up temporary files...")
    for archive in archives_to_delete: archive.unlink()
    shutil.rmtree(unpacked_dir)
    print(f"Collected {file_count} PyPI .py files.")

def generate_synthetic_non_halting():
    create_directory(SYNTHETIC_DEST)
    for i in range(NUM_SYNTHETIC):
        name, code = NON_HALTING_PATTERNS[i % len(NON_HALTING_PATTERNS)]
        (SYNTHETIC_DEST / f"{name}_{i}.py").write_text(code)
    print(f"Generated {NUM_SYNTHETIC} synthetic non-halting files.")

def copy_paradoxes_and_classify():
    create_directory(PARADOXES_DEST); create_directory(COMPLEX_DIR); create_directory(HALTING_DIR)
    if not PROJECT_SCRIPTS_DIR.exists(): return
    halting_s = ["bounded_loop.py", "dynamic_input.py", "halting.py", "self_referential.py", "simple_halting.py"]
    non_halting_s = ["complex_non_halting.py", "final_paradox.py", "mutating_paradox_A.py", "mutating_paradox_A_revised.py", "mutating_paradox_final_test.py", "non_halting.py", "obfuscated_paradox.py", "paradox.py", "polymorphic_termination_paradox.py", "semantic_paradox_A.py", "truly_obfuscated_paradox.py"]
    complex_s = ["ackermann.py", "collatz_conjecture.py"]
    for script in PROJECT_SCRIPTS_DIR.glob("*.py"):
        if script.name in halting_s: shutil.copy(script, HALTING_DIR / script.name)
        elif script.name in non_halting_s: shutil.copy(script, PARADOXES_DEST / script.name)
        elif script.name in complex_s: shutil.copy(script, COMPLEX_DIR / script.name)
    print("Copied and classified adversarial scripts.")

def setup_complex():
    create_directory(COMPLEX_DIR)
    print("Note: Add curated complex cases to 'benchmark_suite/complex/'")

def analyze_file(args):
    file_path, name, expected_result = args
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        program_code = file_path.read_text(encoding='utf-8', errors='ignore')
        analyzer_result, _ = analyze_halting(program_code)
        
        is_correct = False
        if name == "halting":
            if analyzer_result == "halts": is_correct = True
        elif name == "non-halting":
            if analyzer_result in ["does not halt", "impossible to determine"]: is_correct = True
        elif name == "complex":
            if analyzer_result in ["impossible to determine", "does not halt"]: is_correct = True
        
        return (is_correct, file_path.name, analyzer_result)
    except Exception:
        return (False, file_path.name, "error")
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

# --- Main Benchmark Execution Logic ---

def run_benchmark(force_rebuild=False):
    """Builds the corpus if needed, then runs the analyzer and calculates the score."""
    if force_rebuild and BENCHMARK_DIR.exists():
        print("--- Force-rebuilding corpus: Deleting existing suite... ---")
        shutil.rmtree(BENCHMARK_DIR)

    if not BENCHMARK_DIR.exists():
        print("--- Phase 1: Building Benchmark Corpus ---")
        create_directory(BENCHMARK_DIR)
        collect_stdlib()
        download_and_unpack_pypi()
        generate_synthetic_non_halting()
        copy_paradoxes_and_classify()
        setup_complex()
    else:
        print("--- Phase 1: Found existing benchmark suite. Skipping build. ---")
        print("(Use --rebuild flag to force a fresh build)")
    
    print("\n--- Phase 2: Running Analyzer & Calculating Score ---")
    overall_total = 0
    overall_processed = 0
    overall_mismatches = 0
    overall_correct = 0

    category_map = {
        "halting": (HALTING_DIR, "halts"),
        "non-halting": (NON_HALTING_DIR, "does not halt"),
        "complex": (COMPLEX_DIR, "impossible to determine")
    }

    # Precompute overall total
    for name, (category_dir, expected_result) in category_map.items():
        if category_dir.exists():
            files_in_category = list(category_dir.rglob("*.py"))
            overall_total += len(files_in_category)

    start_time = time.time()
    update_interval = max(1, int(overall_total * 0.001))  # 0.1%
    last_updated_processed = 0

    for name, (category_dir, expected_result) in category_map.items():
        if not category_dir.exists(): continue
        print(f"\nStarting analysis for category: '{name}'...")
        files_in_category = list(category_dir.rglob("*.py"))
        cat_total = len(files_in_category)
        
        if cat_total == 0: continue
        
        args_list = [(file_path, name, expected_result) for file_path in files_in_category]
        
        category_processed = 0
        category_mismatches = 0
        mismatches = []

        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(analyze_file, args_list)
            
            for result in results:
                is_correct, filename, analyzer_result = result
                category_processed += 1
                overall_processed += 1
                if is_correct:
                    overall_correct += 1
                else:
                    category_mismatches += 1
                    overall_mismatches += 1
                    mismatches.append((filename, analyzer_result))
                
                # Check if we should update display
                if (overall_processed - last_updated_processed >= update_interval or 
                    overall_processed == overall_total or 
                    category_processed == cat_total):
                    display_progress(name, expected_result, overall_total, overall_processed, overall_mismatches, start_time,
                                     cat_total, category_processed, category_mismatches, mismatches)
                    last_updated_processed = overall_processed
        
        # Clear screen after category
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
        
        print(f"Completed category '{name}' with {category_mismatches} mismatches.")
        if mismatches:
            print("Mismatches:")
            for filename, analyzer_result in mismatches:
                print(f"  MISMATCH: {filename} -> Expected '{expected_result}', Got '{analyzer_result}'")
        else:
            print("No mismatches.")
    
    if overall_total > 0:
        percentage = (overall_correct / overall_total) * 100
        print(f"\n--- Practical Success Rate: {percentage:.2f}% ({overall_correct} of {overall_total} files passed) ---")
    else:
        print("\nNo files were found in the benchmark suite to analyze.")

def display_progress(category, expected, overall_total, overall_proc, overall_mis, start_time,
                      cat_total, cat_proc, cat_mis, mis_list):
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()
    
    elapsed = time.time() - start_time
    if overall_proc > 0:
        time_per_file = elapsed / overall_proc
        eta = time_per_file * (overall_total - overall_proc)
    else:
        eta = 0
    
    print("Benchmark Analysis Progress")
    print("----------------------------")
    print(f"Overall:")
    print(f"  Processed: {overall_proc}/{overall_total} ({overall_proc/overall_total*100:.1f}%)")
    print(f"  Mismatches: {overall_mis}")
    print(f"  Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s")
    
    print(f"\nCurrent Category: {category}")
    print(f"  Processed: {cat_proc}/{cat_total} ({cat_proc/cat_total*100:.1f}%)")
    print(f"  Mismatches: {cat_mis}")
    
    if mis_list:
        print("\nRecent Mismatches (last 5):")
        for filename, analyzer_result in mis_list[-5:]:
            print(f"  {filename}: Expected '{expected}', Got '{analyzer_result}'")
    if len(mis_list) > 5:
        print(f"  ... and {len(mis_list)-5} more")

    sys.stdout.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Halting Analyzer benchmark.")
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help="Force a complete rebuild of the benchmark suite, deleting the old one."
    )
    args = parser.parse_args()
    
    run_benchmark(force_rebuild=args.rebuild)
    
    print("\n--- Benchmark Automation Complete ---")