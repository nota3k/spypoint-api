"""Helper to regenerate models from the OpenAPI spec using datamodel-code-generator.

Moved from `scripts/regen_models.py` as part of cleanup; behaviour unchanged.
"""
import shutil
import subprocess
from pathlib import Path

SPEC = Path(__file__).parent.parent / "spec" / "spypoint.openapi.json"
OUT = Path(__file__).parent.parent / "spypointapi" / "models" / "_generated_auto.py"


def main() -> None:
    if not SPEC.exists():
        print("Spec not found:", SPEC)
        return
    if shutil.which("datamodel-codegen") is None:
        print("datamodel-codegen not found in PATH. Install with pip install datamodel-code-generator")
        return

    cmd = [
        "datamodel-codegen",
        "--input",
        str(SPEC),
        "--input-file-type",
        "openapi",
    "--output",
    str(OUT),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--openapi-scopes",
        "paths",
        "--extra-fields",
        "allow",
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
