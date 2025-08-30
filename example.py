"""Example runner moved to `examples/example.py`.

Run `python -m examples.example` or open `examples/example.py` for a working example.
"""

from pathlib import Path

THIS = Path(__file__).absolute()
EX = THIS.parent / "examples" / "example.py"

if __name__ == "__main__":
    print("Example moved to:", EX)
