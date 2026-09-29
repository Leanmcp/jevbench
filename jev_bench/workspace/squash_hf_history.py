"""Collapse the Hugging Face dataset's history into a single commit.

Earlier uploads of Leanmcp/jevbench contained files that are no longer part of
the release (the harness code, and a provenance line with a local username).
Deleting them in a new commit leaves them readable in the commit history. This
script squashes the main branch so only the current files remain.

Run it after the corrected upload and before re-creating the v0.1 tag:
    time uv run workspace/squash_hf_history.py
"""

from huggingface_hub import HfApi

REPO_ID = "Leanmcp/jevbench"

api = HfApi()
api.super_squash_history(
    repo_id=REPO_ID,
    repo_type="dataset",
    commit_message="JevBench v0.1: cases and predictions",
)
files = api.list_repo_files(REPO_ID, repo_type="dataset")
print(f"Squashed {REPO_ID}. {len(files)} files on main.")
leftover = [f for f in files if f.startswith("workspace/") or f in ("pyproject.toml", "uv.lock")]
if leftover:
    raise SystemExit(f"code files still present: {leftover}")
print("No code files on main.")
