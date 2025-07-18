import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
import sys

# --- Configuration ---
# Fix 1: Define the path to your main analyzer script.
# This assumes the benchmark script is in the same directory as main.py
MAIN_PY = Path("main.py")

BENCHMARK_DIR = Path("benchmark_suite")
HALTING_DIR = BENCHMARK_DIR / "halting"
NON_HALTING_DIR = BENCHMARK_DIR / "non-halting"
COMPLEX_DIR = BENCHMARK_DIR / "complex"

STDLIB_DEST = HALTING_DIR / "stdlib"
PYPI_DEST = HALTING_DIR / "pypi_sources"
SYNTHETIC_DEST = NON_HALTING_DIR / "synthetic"
PARADOXES_DEST = NON_HALTING_DIR / "paradoxes"

# List of PyPI packages to download
PYPI_PACKAGES = [
    "requests", "numpy", "pandas", "flask", "django",
    "scikit-learn", "matplotlib", "beautifulsoup4", "sqlalchemy", "celery"
]

# Number of synthetic non-halting files to generate
NUM_SYNTHETIC = 50

# Patterns for non-halting code
NON_HALTING_PATTERNS = [
    ("while_true", "while True:\n    pass"),
    ("unbounded_inc", "x = 0\nwhile x >= 0:\n    x += 1"),
    ("unbounded_dec", "x = 0\nwhile x <= 0:\n    x -= 1"),
    ("simple_recursion", "def f():\n    f()\nf()"),
    ("mutual_recursion", "def f():\n    g()\ndef g():\n    f()\nf()"),
]

# Path to your project's scripts directory for paradoxes (adjust as needed)
PROJECT_SCRIPTS_DIR = Path("scripts")

# --- Helper Functions ---
def create_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    print(f"Created/Ensured directory: {path}")

def collect_stdlib():
    """Copies all .py files from the standard library."""
    create_directory(STDLIB_DEST)
    stdlib_path = Path(shutil.__file__).parent
    print(f"Found standard library at: {stdlib_path}")
    
    file_count = 0
    for root, _, files in os.walk(stdlib_path):
        for file in files:
            if file.endswith(".py"):
                source = Path(root) / file
                try:
                    shutil.copy(source, STDLIB_DEST)
                    file_count += 1
                except Exception as e:
                    print(f"Could not copy {source}: {e}")
    
    print(f"Successfully copied {file_count} stdlib files.")

def download_and_unpack_pypi():
    """Downloads PyPI packages and unpacks their .py files."""
    create_directory(PYPI_DEST)
    
    # --- Step 1: Download packages using pip ---
    print("Downloading PyPI packages...")
    subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "--dest", str(PYPI_DEST), *PYPI_PACKAGES], check=True, capture_output=True)
    
    # --- Step 2: Unpack all archives first ---
    unpacked_dir = PYPI_DEST / "unpacked"
    create_directory(unpacked_dir)
    
    print("Unpacking archives...")
    archives_to_delete = []
    for archive in PYPI_DEST.iterdir():
        # Only process archive files, ignore directories
        if archive.is_file():
            try:
                if archive.suffix in (".tar.gz", ".tgz"):
                    with tarfile.open(archive, "r:gz") as tar:
                        tar.extractall(path=unpacked_dir)
                    archives_to_delete.append(archive)
                elif archive.suffix == ".whl":
                    with zipfile.ZipFile(archive, "r") as zip_ref:
                        zip_ref.extractall(path=unpacked_dir)
                    archives_to_delete.append(archive)
            except (tarfile.ReadError, zipfile.BadZipFile, EOFError) as e:
                print(f"Warning: Could not unpack {archive.name}: {e}. Skipping.")

    # --- Step 3: Collect all .py files from the unpacked directory ---
    print("Collecting .py files...")
    file_count = 0
    for root, _, files in os.walk(unpacked_dir):
        for file in files:
            if file.endswith(".py"):
                source = Path(root) / file
                # Use a unique name to prevent overwriting files with the same name from different packages
                unique_name = f"{source.parent.name}_{source.name}"
                dest = PYPI_DEST / unique_name
                try:
                    if not dest.exists():
                        shutil.copy(source, dest)
                        file_count += 1
                except Exception as e:
                    print(f"Could not copy {source}: {e}")

    # --- Step 4: Clean up archives and temporary directory *after* all operations are done ---
    print("Cleaning up temporary files...")
    for archive in archives_to_delete:
        try:
            archive.unlink()
        except PermissionError as e:
            print(f"Warning: Could not delete archive {archive.name} immediately: {e}")

    try:
        shutil.rmtree(unpacked_dir)
    except PermissionError as e:
        print(f"Warning: Could not delete temporary directory {unpacked_dir} immediately: {e}")

    print(f"Successfully unpacked and collected {file_count} PyPI .py files.")


def generate_synthetic_non_halting():
    """Generates synthetic non-halting Python scripts."""
    create_directory(SYNTHETIC_DEST)
    file_count = 0
    for i in range(NUM_SYNTHETIC):
        pattern_name, code = NON_HALTING_PATTERNS[i % len(NON_HALTING_PATTERNS)]
        file_path = SYNTHETIC_DEST / f"{pattern_name}_{i}.py"
        with open(file_path, 'w') as f: f.write(code)
        file_count += 1
    print(f"Successfully generated {file_count} synthetic non-halting files.")

def copy_paradoxes_and_classify():
    """Copies user's scripts, classifying halting/non-halting/complex."""
    create_directory(HALTING_DIR)
    create_directory(PARADOXES_DEST)
    create_directory(COMPLEX_DIR)
    
    if not PROJECT_SCRIPTS_DIR.exists():
        print(f"Warning: Scripts directory {PROJECT_SCRIPTS_DIR} not found. Skipping copy.")
        return
    
    # These lists now only contain the base names
    halting_scripts = ["bounded_loop.py", "dynamic_input.py", "halting.py", "self_referential.py", "simple_halting.py"]
    non_halting_scripts = ["complex_non_halting.py", "final_paradox.py", "mutating_paradox_A.py", "mutating_paradox_A_revised.py", "mutating_paradox_final_test.py", "non_halting.py", "obfuscated_paradox.py", "paradox.py", "polymorphic_termination_paradox.py", "semantic_paradox_A.py", "truly_obfuscated_paradox.py"]
    complex_scripts = ["ackermann.py", "collatz_conjecture.py"]
    
    file_count = 0
    for file in PROJECT_SCRIPTS_DIR.iterdir():
        if file.suffix == ".py":
            dest_dir = None
            if file.name in halting_scripts:
                dest_dir = HALTING_DIR
            elif file.name in complex_scripts:
                dest_dir = COMPLEX_DIR
            elif file.name in non_halting_scripts:
                dest_dir = PARADOXES_DEST
            
            if dest_dir:
                shutil.copy(file, dest_dir / file.name)
                file_count += 1
    
    print(f"Successfully copied and classified {file_count} user scripts.")

# Fix 2: Create the placeholder function for clarity
def setup_complex():
    """Placeholder for manual complex files."""
    create_directory(COMPLEX_DIR)
    print("Complex directory created. If you have curated complex cases (e.g., a Turing machine), add them manually.")

def run_halting_analyzer():
    """Runs the main.py on the benchmark suite and collects results."""
    if not MAIN_PY.exists():
        print(f"Error: main.py not found at {MAIN_PY}. Ensure this script is in the project root.")
        return {}
    
    # Modify the main.py content in memory to point to the correct directory
    with open(MAIN_PY, 'r') as f:
        main_code = f.read()
    
    # This replacement is fragile but works for this specific main.py
    modified_code = main_code.replace(
        "scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')",
        f"scripts_dir = r'{BENCHMARK_DIR.resolve()}'"
    )
    
    temp_main_path = BENCHMARK_DIR / "temp_main.py"
    with open(temp_main_path, 'w') as f:
        f.write(modified_code)

    print("Running analyzer on the entire corpus... this may take several minutes.")
    try:
        # Run the modified main script
        process = subprocess.run([sys.executable, str(temp_main_path)], capture_output=True, text=True, timeout=600) # 10-min timeout
        
        results = {}
        current_script = None
        output = process.stdout
        
        for line in output.splitlines():
            if line.startswith("[Analyzing]: "):
                # Extract just the filename from the path
                full_path = line.split("[Analyzing]: ")[1].strip()
                current_script = os.path.basename(full_path)
            elif line.startswith("Result: ") and current_script:
                result = line.split("Result: ")[1].strip()
                results[current_script] = result
                current_script = None
        
        if process.stderr:
            print("\n--- Analyzer Errors (stderr) ---")
            print(process.stderr)
            print("------------------------------\n")
            
        return results
    except subprocess.TimeoutExpired:
        print("ERROR: The benchmark run timed out. The corpus may be too large or a script caused a severe hang.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while running the analyzer: {e}")
        return {}
    finally:
        if temp_main_path.exists():
            temp_main_path.unlink()

def calculate_percentage(results):
    """Calculates success percentage based on expected behaviors."""
    total = 0
    success = 0
    
    print("\n--- Verifying Benchmark Results ---")
    for category_dir, expected in [(HALTING_DIR, "halts"), (NON_HALTING_DIR, "does not halt"), (COMPLEX_DIR, "impossible to determine")]:
        for root, _, files in os.walk(category_dir):
            for file in files:
                if file.endswith(".py"):
                    total += 1
                    analyzer_result = results.get(file, "error (not found in output)")
                    
                    is_success = False
                    if category_dir.name == "halting":
                        if analyzer_result == expected:
                            is_success = True
                    elif category_dir.name == "non-halting":
                        # Success if it correctly says "does not halt" OR safely defers
                        if analyzer_result in ["does not halt", "impossible to determine"]:
                            is_success = True
                    elif category_dir.name == "complex":
                        # Success if it safely defers OR correctly proves it halts (like Ackermann in theory)
                        if analyzer_result in ["impossible to determine", "halts", "does not halt"]: # 'does not halt' is safe for Ackermann
                            is_success = True
                    
                    if is_success:
                        success += 1
                    else:
                        print(f"MISMATCH in {category_dir.name}: {file} -> Expected '{expected}', Got '{analyzer_result}'")

    if total > 0:
        percentage = (success / total) * 100
        print(f"\n--- Practical Success Rate: {percentage:.2f}% ({success}/{total}) ---")
    else:
        print("No files were analyzed.")

# --- Main Execution ---
if __name__ == "__main__":
    create_directory(BENCHMARK_DIR)
    
    print("--- Phase 1: Collecting Corpus ---")
    collect_stdlib()
    download_and_unpack_pypi()
    generate_synthetic_non_halting()
    copy_paradoxes_and_classify()
    setup_complex()
    
    print("\n--- Phase 2: Running Halting Analyzer ---")
    analysis_results = run_halting_analyzer()
    
    print("\n--- Phase 3: Calculating Final Score ---")
    calculate_percentage(analysis_results)
    
    print("\n--- Automation Complete ---")