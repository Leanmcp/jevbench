"""Download and verify the jev-bench source datasets at pinned revisions.

Reads ../sources.json, fetches every listed file at its pinned commit, then
measures what actually arrived: byte size, sha256, row count, observed columns
and label distribution. Writes ../data/MANIFEST.measured.json.

It downloads and measures. It does not adapt records, call a model, or spend
money on an API. Nothing is printed from the record text itself, because several
of these sets contain adversarial prompts that should be treated as data.

Usage:
    uv run workspace/download.py                      # every source
    uv run workspace/download.py --only medmcqa       # repeatable
    uv run workspace/download.py --skip scienceqa     # repeatable
    uv run workspace/download.py --tier mcq           # repeatable
    uv run workspace/download.py --list               # plan only, no download
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.json"
DATA = ROOT / "data"
OUT = DATA / "MANIFEST.measured.json"

# Label distributions are read for stratified sampling in step 3. Reading a
# whole column is cheap for text sets and expensive for the image sets, so cap
# the sets where a column read would pull image bytes along with it.
SKIP_LABEL_SCAN = {"vqa_rad", "scienceqa"}
MAX_VOCAB_REPORTED = 200


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json_any(path: Path):
    """Aegis ships .json that may be a JSON array or one object per line."""
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("["):
        return json.loads(text), "json_array"
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return rows, "json_lines"


def measure_parquet(path: Path, src: dict) -> dict:
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(path)
    info: dict = {
        "row_count": pf.metadata.num_rows,
        "row_groups": pf.metadata.num_row_groups,
        "columns_observed": list(pf.schema_arrow.names),
    }
    gold = src.get("gold_field")
    if gold and src["key"] not in SKIP_LABEL_SCAN and gold in info["columns_observed"]:
        col = pq.read_table(path, columns=[gold])[gold].to_pylist()
        info["label_distribution"] = summarise_labels(col)
    return info


def measure_jsonl(path: Path, src: dict) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return finish_rows(rows, src)


def measure_json(path: Path, src: dict) -> dict:
    rows, detected = load_json_any(path)
    if not isinstance(rows, list):
        return {"row_count": None, "error": f"top level is {type(rows).__name__}, expected a list"}
    info = finish_rows(rows, src)
    info["detected_format"] = detected
    return info


def measure_csv(path: Path, src: dict) -> dict:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return finish_rows(rows, src)


def finish_rows(rows: list, src: dict) -> dict:
    info: dict = {"row_count": len(rows)}
    if rows and isinstance(rows[0], dict):
        seen: dict[str, None] = {}
        for row in rows[:1000]:
            for key in row:
                seen.setdefault(key, None)
        info["columns_observed"] = list(seen)
        gold = src.get("gold_field")
        if gold and gold in seen:
            info["label_distribution"] = summarise_labels([r.get(gold) for r in rows])
    return info


def summarise_labels(values: list) -> dict:
    counts = collections.Counter(
        v if isinstance(v, (str, int, bool, type(None))) else repr(v) for v in values
    )
    out = {
        "n_distinct": len(counts),
        "n_null": counts.get(None, 0),
    }
    if len(counts) <= MAX_VOCAB_REPORTED:
        out["counts"] = {str(k): v for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))}
    else:
        out["note"] = f"{len(counts)} distinct values, above the {MAX_VOCAB_REPORTED} reporting cap"
        out["most_common"] = {str(k): v for k, v in counts.most_common(20)}
    return out


MEASURERS = {
    "parquet": measure_parquet,
    "jsonl": measure_jsonl,
    "json_array": measure_json,
    "json_lines_or_array": measure_json,
    "csv": measure_csv,
}


def select(sources: list[dict], args) -> list[dict]:
    chosen = sources
    if args.only:
        chosen = [s for s in chosen if s["key"] in set(args.only)]
    if args.tier:
        chosen = [s for s in chosen if s["tier"] in set(args.tier)]
    if args.skip:
        chosen = [s for s in chosen if s["key"] not in set(args.skip)]
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], metavar="KEY")
    ap.add_argument("--skip", action="append", default=[], metavar="KEY")
    ap.add_argument("--tier", action="append", default=[], metavar="TIER")
    ap.add_argument("--list", action="store_true", help="print the plan and exit")
    args = ap.parse_args()

    manifest = json.loads(SOURCES.read_text(encoding="utf-8"))
    sources = select(manifest["sources"], args)
    if not sources:
        print("No sources selected. Known keys: " + ", ".join(s["key"] for s in manifest["sources"]))
        return 2

    print(f"jev-bench download, manifest pinned {manifest['pinned_on']}")
    print(f"{len(sources)} of {len(manifest['sources'])} sources selected: " + ", ".join(s['key'] for s in sources))
    print("Cache and copies land in " + str(DATA))
    if args.list:
        for s in sources:
            print(f"  {s['key']:22} {s['tier']:13} {s['task_type']:7} {s['hf_repo']}@{s['revision'][:12]}  {len(s['files'])} file(s)  {s['license']}")
        return 0

    from huggingface_hub import hf_hub_download

    DATA.mkdir(parents=True, exist_ok=True)
    measured: list[dict] = []
    failures: list[str] = []

    for src in sources:
        key = src["key"]
        print(f"\n=== {key}  ({src['hf_repo']}@{src['revision'][:12]}, {src['license']}) ===")
        dest = DATA / key
        dest.mkdir(parents=True, exist_ok=True)
        entry = {
            "key": key,
            "hf_repo": src["hf_repo"],
            "revision": src["revision"],
            "license": src["license"],
            "tier": src["tier"],
            "task_type": src["task_type"],
            "exposure": src["exposure"],
            "files": [],
            "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        for rel in src["files"]:
            t0 = time.time()
            try:
                cached = hf_hub_download(
                    repo_id=src["hf_repo"],
                    filename=rel,
                    revision=src["revision"],
                    repo_type="dataset",
                    local_dir=dest,
                )
            except Exception as exc:  # noqa: BLE001 - report and continue to the next source
                print(f"  FAILED {rel}: {type(exc).__name__}: {exc}")
                failures.append(f"{key}/{rel}")
                entry["files"].append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
                continue

            path = Path(cached)
            size = path.stat().st_size
            digest = sha256_of(path)
            print(f"  {rel}")
            print(f"    {size:,} bytes  sha256={digest[:16]}...  {time.time() - t0:.1f}s")

            finfo = {"path": rel, "local_path": str(path.relative_to(ROOT)), "bytes": size, "sha256": digest}
            measurer = MEASURERS.get(src["format"])
            if measurer is None:
                finfo["error"] = f"no measurer for format {src['format']!r}"
            else:
                try:
                    finfo.update(measurer(path, src))
                except Exception as exc:  # noqa: BLE001
                    finfo["error"] = f"measure failed: {type(exc).__name__}: {exc}"
                    print(f"    measure failed: {type(exc).__name__}: {exc}")

            if "row_count" in finfo:
                print(f"    rows={finfo['row_count']:,}")
            observed = finfo.get("columns_observed")
            if observed is not None:
                expected = set(src.get("columns") or [])
                missing = sorted(expected - set(observed))
                extra = sorted(set(observed) - expected)
                if missing:
                    print(f"    WARNING columns in manifest but not in file: {missing}")
                if extra:
                    print(f"    note: columns in file but not in manifest: {extra}")
                finfo["columns_missing_vs_manifest"] = missing
                finfo["columns_extra_vs_manifest"] = extra

            dist = finfo.get("label_distribution")
            if dist:
                print(f"    gold field {src['gold_field']!r}: {dist['n_distinct']} distinct, {dist['n_null']} null")
                exp_classes = src.get("expected_n_classes")
                if exp_classes and dist["n_distinct"] != exp_classes:
                    print(f"    WARNING expected {exp_classes} classes, observed {dist['n_distinct']}")
                if "counts" in dist and dist["n_distinct"] <= 12:
                    for label, n in dist["counts"].items():
                        print(f"      {label!r}: {n:,}")

            entry["files"].append(finfo)
        measured.append(entry)

    payload = {
        "manifest_version": manifest["manifest_version"],
        "pinned_on": manifest["pinned_on"],
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "selected": [s["key"] for s in sources],
        "failures": failures,
        "sources": measured,
    }
    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    if existing:
        # Keep measurements for sources this run did not select.
        kept = [e for e in existing.get("sources", []) if e["key"] not in {s["key"] for s in sources}]
        payload["sources"] = kept + measured
        payload["sources"].sort(key=lambda e: e["key"])
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    total = sum(f.get("bytes", 0) for e in measured for f in e["files"])
    rows = sum(f.get("row_count") or 0 for e in measured for f in e["files"])
    print(f"\nWrote {OUT.relative_to(ROOT)}")
    print(f"{len(measured)} sources, {total:,} bytes downloaded, {rows:,} rows measured")
    if failures:
        print(f"{len(failures)} file(s) failed: " + ", ".join(failures))
        return 1
    print("Next: step 3 builds the adapter from sources.json model_visible allowlists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
