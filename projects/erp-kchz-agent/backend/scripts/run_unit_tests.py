from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_module(path: Path):
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures = 0
    tests_dir = ROOT / "tests"
    for path in sorted(tests_dir.glob("test_*.py")):
        try:
            module = load_module(path)
        except Exception:
            failures += 1
            print(f"FAIL {path.name}: module import failed")
            traceback.print_exc()
            continue

        for name in sorted(dir(module)):
            if not name.startswith("test_"):
                continue
            test_func = getattr(module, name)
            if not callable(test_func):
                continue
            try:
                test_func()
                print(f"PASS {path.name}::{name}")
            except Exception:
                failures += 1
                print(f"FAIL {path.name}::{name}")
                traceback.print_exc()

    if failures:
        print(f"{failures} test failure(s)")
        return 1
    print("all tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
