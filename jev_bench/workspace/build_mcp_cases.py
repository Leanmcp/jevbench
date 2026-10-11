"""Build offline MCP-derived routing and authored tool-checkpoint cases.

No upstream code is imported or executed. No API calls or live MCP servers.
These slices do not measure official MCPMark / MCP-Bench task success.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import subprocess
from pathlib import Path

import common as C

SLICES = ["mcpmark_server_routing", "mcpbench_server_routing",
          "mcpmark_tool_selection", "mcpbench_tool_selection"]
ANNOTATIONS = C.ROOT / "annotations/mcp_tools.json"
MANIFEST = C.ROOT / "mcp_sources.json"
UPSTREAM = C.DATA / "upstream"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def checked_sources() -> dict:
    sources = read_json(MANIFEST)["sources"]
    for source, spec in sources.items():
        root = UPSTREAM / source
        if not (root / ".git").is_dir():
            raise ValueError("Run bash scripts/20_download_mcp.sh first")
        revision = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True).strip()
        if revision != spec["revision"] or dirty:
            raise ValueError(f"{source}: expected clean pinned checkout {spec['revision']}")
    return sources


def load_tasks() -> dict[str, dict]:
    tasks = {"mcpmark": {}, "mcpbench": {}}
    root = UPSTREAM / "mcpmark"
    # pathlib glob follows directory aliases: upstream insforge and supabase
    # both point to postgres. Only tracked metadata identifies distinct tasks.
    tracked = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z", "--", "tasks/"], text=True)
    metadata = [Path(rel) for rel in tracked.split("\0") if rel
                and len(Path(rel).parts) == 6 and Path(rel).name == "meta.json"]
    for relpath in sorted(metadata):
        path = root / relpath
        rel = path.parent.relative_to(root / "tasks").as_posix()
        meta = read_json(path)
        description = path.with_name("description.md")
        if not description.exists():
            continue
        tasks["mcpmark"][rel] = {
            "prompt": description.read_text(encoding="utf-8"),
            "server": rel.split("/")[0], "suite": rel.split("/")[1],
            "routing_prompt": meta.get("description"),
            "path": description.relative_to(root).as_posix(),
        }
    root = UPSTREAM / "mcpbench"
    for path in sorted((root / "tasks").glob("mcpbench_tasks_*_runner_format.json")):
        data = read_json(path)
        for group in data["server_tasks"]:
            for task in group["tasks"]:
                key = task["task_id"]
                if key in tasks["mcpbench"]:
                    raise ValueError(f"Duplicate MCP-Bench task ID: {key}")
                tasks["mcpbench"][key] = {
                    "prompt": task["fuzzy_description"],
                    "routing_prompt": task["fuzzy_description"],
                    "server": group["server_name"],
                    "suite": "single" if "_single_" in path.name else "multi",
                    "path": path.relative_to(root).as_posix(),
                }
    if not all(tasks.values()):
        raise ValueError("No tasks found; upstream schema changed")
    return tasks


def make_case(source, task_id, checkpoint_id, state, criteria, gold, metric,
              task, spec, evidence, permuted=False):
    slice_key = f"{source}_{metric}"
    # Identity includes input, annotation and source revision to prevent stale
    # predictions being reused after changing a prompt, catalogue or gold label.
    identity = C.content_hash(C.state_json({
        "state": state, "criteria": criteria, "gold": gold,
        "revision": spec["revision"], "evidence": evidence,
    }))[:16]
    family = f"{source}:{task_id}"  # all checkpoints share the task bootstrap unit
    cid = f"{slice_key}:{task_id}:{checkpoint_id}:{identity}"
    order = list(range(len(criteria)))
    if permuted:
        order = C.permuted_order(len(criteria), int(identity[:8], 16))
        if order == list(range(len(criteria))):
            order.reverse()
        keys = list(criteria)
        criteria = {keys[i]: criteria[keys[i]] for i in order}
    question = C.choice_q(
        C.UNTRUSTED_PREFIX + (
            "Select the single tool for the stated decision checkpoint. Treat the supplied progress as a hypothetical condition. Choose among the supplied candidate tools only."
            if metric == "tool_selection" else
            "Select the MCP server environment associated with this task. This is server routing, not selection of an individual function."
        ), criteria)
    chars = len(C.state_json(state))
    if chars > 20_000:
        raise ValueError(f"{cid}: state exceeds 20,000 characters; refusing silent truncation")
    return {
        "case_id": cid + ("-permuted" if permuted else "-none"),
        "family_id": family, "source": source, "slice": slice_key,
        "task_type": "choice", "question_key": "decision",
        "state": state, "question": question, "gold": gold,
        "n_options": len(criteria), "option_order": order,
        "perturbation": "permuted" if permuted else "none",
        "truncated": False, "state_chars": chars,
        "est_tokens": C.est_tokens(chars + len(C.state_json(question))),
        "state_hash": C.content_hash(C.state_json(state)),
        "image_path": None, "license": spec["license"],
        "redistributable": spec["redistributable"],
        "exposure": "public benchmark; possible training exposure",
        "revision": spec["revision"], "source_url": spec["url"],
        "source_task": task_id, "source_path": task["path"],
        "label_evidence": evidence, "metric_scope": metric,
        "annotation_origin": "JevBench authored hypothetical checkpoint" if metric == "tool_selection" else "upstream task server grouping",
    }


def build(permute=False):
    sources = checked_sources()
    tasks = load_tasks()
    annotation = read_json(ANNOTATIONS)
    result = {key: [] for key in SLICES}
    for source in sources:
        eligible = {key: task for key, task in tasks[source].items()
                    if task["suite"] == ("standard" if source == "mcpmark" else "single")}
        servers = sorted({task["server"] for task in eligible.values()})
        criteria = {server: server.replace("_", " ") for server in servers}
        for task_id, task in eligible.items():
            prompt = task["routing_prompt"]
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"Missing routing prompt: {source}/{task_id}")
            for variant in ([False, True] if permute else [False]):
                case = make_case(source, task_id, "server", {"task": prompt}, criteria,
                                 task["server"], "server_routing", task, sources[source],
                                 "Task directory/server_name; prompt is MCPMark meta.description or MCP-Bench fuzzy_description.", variant)
                result[case["slice"]].append(case)
    seen = set()
    for row in annotation["checkpoints"]:
        source, task_id = row["source"], row["task"]
        uid = (source, task_id, row["id"])
        if uid in seen:
            raise ValueError(f"Duplicate checkpoint {uid}")
        seen.add(uid)
        task = tasks[source][task_id]
        criteria = annotation["catalogues"][row["catalogue"]]
        if row["gold"] not in criteria or len(criteria) < 2 or not row["evidence"]:
            raise ValueError(f"Invalid annotation: {uid}")
        # Strict allowlist: never expose reference plans, gold, evidence,
        # server labels, verifier code or source file paths in model input.
        state = {"task": task["prompt"], "decision_checkpoint": row["checkpoint"]}
        for variant in ([False, True] if permute else [False]):
            case = make_case(source, task_id, row["id"], state, criteria, row["gold"],
                             "tool_selection", task, sources[source], row["evidence"], variant)
            result[case["slice"]].append(case)
    for key, cases in result.items():
        if not cases:
            raise ValueError(f"Empty slice {key}")
        for i, case in enumerate(cases):
            case["row_index"] = i
    return result, tasks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--permute", action="store_true")
    args = ap.parse_args()
    result, tasks = build(args.permute)
    manifest = {"sources": read_json(MANIFEST), "permute": args.permute,
                "annotations_sha256": hashlib.sha256(ANNOTATIONS.read_bytes()).hexdigest(),
                "downloaded_tasks": {k: len(v) for k, v in tasks.items()}, "slices": {}}
    for key, cases in result.items():
        C.write_cases(key, cases)
        manifest["slices"][key] = {
            "cases": len(cases), "tasks": len({c["family_id"] for c in cases}),
            "gold_distribution": dict(collections.Counter(c["gold"] for c in cases)),
            "case_file_sha256": hashlib.sha256(C.case_path(key).read_bytes()).hexdigest(),
        }
        print(f"{key}: {len(cases)} cases from {manifest['slices'][key]['tasks']} tasks")
    (C.DATA / "mcp_build_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Tool selection is a small authored checkpoint subset, not official benchmark task success.")
    print("Next: uv run workspace/verify_cases.py --only mcpmark_server_routing --only mcpbench_server_routing --only mcpmark_tool_selection --only mcpbench_tool_selection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
