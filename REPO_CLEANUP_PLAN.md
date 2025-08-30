# REPO_CLEANUP_PLAN

Goal
----
Perform a safe, minimal repository cleanup that removes or archives leftover/dead files while preserving the working SDK and tests. This plan will be materialized only after review. No destructive changes are applied until this plan is acknowledged.

Guardrails
----------
- Do NOT delete: `spypoint_api/**`, `spec/spypoint.openapi.json`, `tests/**`, `examples/**`, `pyproject.toml`, `README.md`, `LICENSE`, `.gitignore` unless explicitly approved.
- Create branch `chore/repo-cleanup` and commit in small steps with clear messages.

Actions planned (high level)
---------------------------
1. Inventory: static AST import graph to find reachable modules and candidate dead modules.
2. Static signals: run ruff suggestions (commands recommended) and optionally vulture locally.
3. Non-destructive fixes: apply ruff --fix for unused imports/vars inside `spypoint_api`.
4. Move useful scripts into `examples/`.
5. Remove orphan files (not in guardrail list) such as notebooks, tmp, legacy folders — only after explicit approval.
6. Trim `pyproject.toml` dependencies to the minimal set.
7. Produce `REPO_CLEANUP_REPORT.md` summarizing changes.

Planned files to add now (non-destructive)
---------------------------------------
- `tools/inventory.py` — walks the repo, builds AST import graph and lists candidates.
- Append safe ignores to `.gitignore`.

How to review
-------------
1. Inspect the generated `tools/inventory_result.json` (created by running `tools/inventory.py`).
2. I will update this plan with exact files proposed for deletion/move, with rationale and line references.
3. Only after you approve the plan items will I apply deletions/moves (in commits per the Commit plan below).

Commit plan (exact messages)
---------------------------
1. chore(cleanup): add inventory tool and generate cleanup plan
2. chore(cleanup): ruff autofix unused imports/vars in package
3. chore(cleanup): remove orphan files and vibe-coded folders per plan
4. chore(cleanup): move useful scripts to examples/ and fix imports
5. chore(cleanup): trim pyproject deps to used set
6. chore(cleanup): update .gitignore and write cleanup report

Next step
---------
I'll run the inventory tool and produce `tools/inventory_result.json`. Inspect that file and the proposed deletions before I apply any destructive changes.
