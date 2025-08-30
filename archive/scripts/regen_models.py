"""Archived copy of scripts/regen_models.py moved during cleanup.
This file was moved from scripts/regen_models.py to archive/scripts/regen_models.py
"""
from pathlib import Path

SPEC = Path(__file__).parent.parent / "spec" / "spypoint.openapi.json"

def main():
    print("This file was archived during cleanup. Use tools/regen_models.py instead.")

if __name__ == "__main__":
    main()
