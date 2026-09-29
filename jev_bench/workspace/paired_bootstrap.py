"""Paired bootstrap over shared case identifiers.

The main table reports each model's accuracy with its own interval, computed
independently. Those intervals overlap whenever two models are close, which
understates what the data can settle: all models answered byte-identical cases,
so the per-case correlation between them is available and carries information.

The paired test resamples whole families once and reads BOTH models on the same
resample, so the difference is measured on matched items. Where two models fail
the same hard cases, the paired interval on the difference is much tighter than
the gap between two unpaired intervals.

Also reports the McNemar-style split: on how many cases did exactly one of the
two models get it right. That is the raw material the paired test operates on.

    uv run workspace/paired_bootstrap.py
    uv run workspace/paired_bootstrap.py --runs jev=jev-1.13.0-20260926T133639 --runs djev=djev-full
    uv run workspace/paired_bootstrap.py --format latex

No model calls, no GPU. Reads only the released predictions.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import statistics

import common as C

DEFAULT_RUNS = {
    "Jev 1.13": "jev-1.13.0-20260926T133639",
    "djev-0.1": "djev-full",
    "Laya 421M": "laya-en-full",
}
BOOTSTRAP_N = 2000
SEED = 11


def load(run_id: str) -> dict[str, dict]:
    """case_id -> record, last write wins so a resumed run does not double count."""
    out: dict[str, dict] = {}
    for rec in C.read_jsonl(C.RUNS / run_id / "predictions.jsonl"):
        if not rec.get("error") and not rec.get("parse_error") and rec.get("pred") is not None:
            out[rec["case_id"]] = rec
    return out


def score_of(rec: dict) -> float:
    """Higher is better for choice and noul; for score slices we return the
    negated absolute error so that 'higher is better' holds everywhere and the
    sign of a difference always means the same thing."""
    t = rec["task_type"]
    if t == "choice":
        return 1.0 if str(rec["gold"]) == str(rec["pred"]) else 0.0
    if t == "noul":
        return 1.0 if bool(rec["gold"]) == (float(rec["p_true"]) >= 0.5) else 0.0
    return -abs(int(rec["gold"]) - float(rec["expected_level"]))


def paired(a: dict[str, dict], b: dict[str, dict], slice_key: str) -> dict | None:
    shared = [cid for cid in a if cid in b and a[cid]["slice"] == slice_key]
    if len(shared) < 20:
        return None
    fams: dict[str, list[tuple[float, float]]] = collections.defaultdict(list)
    for cid in shared:
        fams[a[cid]["family_id"]].append((score_of(a[cid]), score_of(b[cid])))
    groups = list(fams.values())

    flat = [p for g in groups for p in g]
    delta = statistics.fmean(x - y for x, y in flat)

    rng = random.Random(SEED)
    deltas = []
    for _ in range(BOOTSTRAP_N):
        pick = [groups[rng.randrange(len(groups))] for _ in range(len(groups))]
        pairs = [p for g in pick for p in g]
        deltas.append(statistics.fmean(x - y for x, y in pairs))
    deltas.sort()
    lo, hi = deltas[int(0.025 * len(deltas))], deltas[int(0.975 * len(deltas))]

    # McNemar split, defined only where the score is 0/1
    a_only = b_only = both = neither = None
    if a[shared[0]]["task_type"] in {"choice", "noul"}:
        a_only = sum(1 for x, y in flat if x > y)
        b_only = sum(1 for x, y in flat if y > x)
        both = sum(1 for x, y in flat if x == y == 1.0)
        neither = sum(1 for x, y in flat if x == y == 0.0)

    return {
        "slice": slice_key,
        "n_cases": len(flat),
        "n_families": len(groups),
        "delta": delta,
        "ci": [lo, hi],
        "excludes_zero": (lo > 0) or (hi < 0),
        "a_only": a_only, "b_only": b_only, "both": both, "neither": neither,
        "task_type": a[shared[0]]["task_type"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", action="append", default=[], metavar="LABEL=RUN_ID")
    ap.add_argument("--format", choices=["text", "latex"], default="text")
    ap.add_argument("--out", default=None, help="write the JSON result here")
    args = ap.parse_args()

    runs = dict(r.split("=", 1) for r in args.runs) if args.runs else DEFAULT_RUNS
    loaded = {label: load(rid) for label, rid in runs.items()}
    for label, recs in loaded.items():
        print(f"{label:12} {len(recs):>6,} usable predictions  ({runs[label]})")

    labels = list(runs)
    pairs = [(labels[i], labels[j]) for i in range(len(labels)) for j in range(i + 1, len(labels))]
    slices = sorted({r["slice"] for recs in loaded.values() for r in recs.values()})

    results: dict[str, list[dict]] = {}
    for la, lb in pairs:
        key = f"{la} - {lb}"
        rows = [r for s in slices if (r := paired(loaded[la], loaded[lb], s))]
        results[key] = rows
        print(f"\n=== {key} ===")
        print(f"{'slice':<26} {'n':>5} {'delta':>8} {'95% paired CI':>20}  {'sig':>4}  A-only/B-only")
        for r in rows:
            ci = f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}]"
            sig = "yes" if r["excludes_zero"] else "no"
            split = f"{r['a_only']}/{r['b_only']}" if r["a_only"] is not None else "n/a (ordinal)"
            print(f"{r['slice']:<26} {r['n_cases']:>5} {r['delta']:>+8.3f} {ci:>20}  {sig:>4}  {split}")

    payload = {
        "runs": runs,
        "bootstrap_resamples": BOOTSTRAP_N,
        "seed": SEED,
        "unit": "family_id",
        "note": ("delta is A minus B on matched cases. For score slices the quantity is "
                 "negated absolute error, so positive always favours A."),
        "pairs": results,
    }
    out = C.RUNS / (args.out or "paired_bootstrap.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out.relative_to(C.ROOT)}")

    if args.format == "latex":
        print("\n% ---- appendix table ----")
        for key, rows in results.items():
            for r in rows:
                print(f"\\texttt{{{r['slice'].replace('_', chr(92)+'_')}}} & {r['n_cases']:,} & "
                      f"{r['delta']:+.3f} & [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] & "
                      f"{'yes' if r['excludes_zero'] else 'no'} & "
                      f"{r['a_only']}/{r['b_only']} \\\\  % {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
