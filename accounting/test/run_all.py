"""
Run all example scripts in test/.
Each example is imported and its main() is called; the DB is reset at the start of each.
"""

import importlib.util
from pathlib import Path
import sys
import traceback

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

LEDGER_DB_PATH = str(TEST_DIR / "ledger.db")

TEST_PREFIX = "test_"
TEST_SUFFIX = ".py"


def discover_examples():
    """Return sorted list of example module names (e.g. example_dinner_reimbursement)."""
    names = []
    for path in TEST_DIR.iterdir():
        if path.name.startswith(TEST_PREFIX) and path.suffix == TEST_SUFFIX:
            names.append(path.name)
    return sorted(names)


def run_one(name: str) -> bool:
    """Load and run main() from the named module. Return True if successful."""
    path = TEST_DIR / f"{name}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        print(f"[FAIL] {name}: could not load")
        return False
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False
    if not hasattr(mod, "main"):
        print(f"[FAIL] {name}: no main()")
        return False
    try:
        mod.main()
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False
    return True


def main() -> int:
    examples = discover_examples()
    if not examples:
        print("No example_*.py modules found in test/")
        return 1
    print(f"Running {len(examples)} example(s): {', '.join(examples)}\n")
    failed = []
    for name in examples:
        if not run_one(name):
            failed.append(name)
    if failed:
        print(f"\nFailed: {', '.join(failed)}")
        return 1
    print(f"\nAll {len(examples)} example(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
