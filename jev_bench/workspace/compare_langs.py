"""English versus translated runs of the OpenRouter decision models.

    uv run workspace/compare_langs.py
    uv run workspace/compare_langs.py --langs zh ar hi vi --variant state

Reads predictions only, no model calls. English is each model's run_id in
models.json; a translated run is <label>-<lang> (state and question translated)
or <label>-<lang>-enq (state translated, question in English), as written by
scripts/45_run_multilingual.sh.

Every number for a model is computed on the same cases: those its English run
and every translated run it has answered without error. Cases the translator
did not deliver are absent from the translated sets, so this pairing keeps
English from being scored on extra, possibly easier, items.

The headline is the mean accuracy over the chosen slices (default: the five
safety slices), each slice weighted equally. The 95% interval on a drop is a
paired bootstrap over families, resampled once and read on both languages.

Writes reports/MULTILINGUAL.md (or MULTILINGUAL_enq.md for --variant state).
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import statistics

import common as C
from score_runs import is_correct

SLICES = ["jailbreak_classification", "prompt_injections", "aegis2", "aegis2_response", "atbench500"]
LANG_NAMES = {"en": "English", "zh": "Chinese", "ar": "Arabic", "hi": "Hindi", "vi": "Vietnamese", "sw": "Swahili", "es": "Spanish", "ta": "Tamil", "kn": "Kannada", "fr": "French", "ru": "Russian"}
BOOTSTRAP_N = 2000


def load(run_id: str) -> dict[str, dict]:
    path = C.RUNS / run_id / "predictions.jsonl"
    if not path.exists():
        return {}
    out = {}
    for r in C.read_jsonl(path):
        if r["slice"] in SLICES and not r.get("error") and r.get("answer_type") == r["task_type"]:
            out[r["case_id"]] = r
    return out


def macro(recs: dict[str, dict], ids: list[str]) -> tuple[float | None, dict[str, float]]:
    per: dict[str, list[float]] = collections.defaultdict(list)
    for cid in ids:
        r = recs[cid]
        per[r["slice"]].append(1.0 if is_correct(r, r["task_type"]) else 0.0)
    by_slice = {k: statistics.fmean(v) for k, v in per.items()}
    return (statistics.fmean(by_slice.values()) if by_slice else None), by_slice


def paired_ci(en: dict, xx: dict, ids: list[str], seed: int = 7) -> tuple[float, float] | None:
    """95% interval on macro(xx) - macro(en), resampling families within each slice."""
    # Per slice, each family reduced once to (sum of correct differences, cases),
    # so a resample is only index picks and two sums.
    fams: dict[str, dict[str, list[int]]] = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for cid in ids:
        f = fams[en[cid]["slice"]][en[cid]["family_id"]]
        f[0] += int(is_correct(xx[cid], xx[cid]["task_type"])) - int(is_correct(en[cid], en[cid]["task_type"]))
        f[1] += 1
    per_slice = [([d for d, _ in g.values()], [n for _, n in g.values()]) for g in fams.values()]
    rng = random.Random(seed)
    diffs = []
    for _ in range(BOOTSTRAP_N):
        per = []
        for d, n in per_slice:
            idx = rng.choices(range(len(d)), k=len(d))
            per.append(sum(d[i] for i in idx) / sum(n[i] for i in idx))
        diffs.append(statistics.fmean(per))
    diffs.sort()
    return diffs[int(0.025 * BOOTSTRAP_N)], diffs[int(0.975 * BOOTSTRAP_N) - 1]


def pct(x: float | None) -> str:
    return "–" if x is None else f"{100 * x:.1f}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--langs", nargs="+", default=["zh", "ar", "hi", "vi", "sw", "es", "ta", "kn", "fr", "ru"])
    ap.add_argument("--variant", choices=["full", "state"], default="full")
    ap.add_argument("--slices", nargs="+", default=SLICES, help="default: the five safety slices")
    ap.add_argument("--no-ci", action="store_true", help="skip the bootstrap, faster")
    args = ap.parse_args()
    SLICES[:] = args.slices
    suffix = "" if args.variant == "full" else "-enq"

    models = json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]
    models = [m for m in models if m.get("endpoint") == "openrouter" and (C.RUNS / m["run_id"]).exists()]

    rows, slice_acc, coverage = [], collections.defaultdict(lambda: collections.defaultdict(list)), []
    langs_seen: list[str] = []
    for m in models:
        en = load(m["run_id"])
        runs = {lang: load(f"{m['label']}-{lang}{suffix}") for lang in args.langs}
        runs = {lang: recs for lang, recs in runs.items() if recs}
        if not en or not runs:
            continue
        langs_seen += [lang for lang in runs if lang not in langs_seen]
        ids = sorted(set(en).intersection(*runs.values()))
        if not ids:
            continue
        print(f"  {m['name']}: {len(ids):,} paired cases, {', '.join(runs)}", flush=True)
        en_acc, en_slices = macro(en, ids)
        row = {"model": m["name"], "n": len(ids), "en": en_acc, "langs": {}}
        for k, v in en_slices.items():
            slice_acc[k]["en"].append(v)
        for lang, recs in runs.items():
            acc, by_slice = macro(recs, ids)
            ci = None if args.no_ci else paired_ci(en, recs, ids)
            row["langs"][lang] = (acc, ci)
            for k, v in by_slice.items():
                slice_acc[k][lang].append(v)
            coverage.append([m["name"], LANG_NAMES.get(lang, lang), len(recs), len(ids)])
        rows.append(row)

    if not rows:
        print(f"No translated runs found (variant {args.variant}). Run scripts/45_run_multilingual.sh first.")
        return 2
    langs = [lang for lang in args.langs if lang in langs_seen]
    rows.sort(key=lambda r: -(r["en"] or 0))

    head = ["model", "cases", "English"] + [LANG_NAMES.get(lang, lang) for lang in langs]
    main_rows = []
    for r in rows:
        cells = [r["model"], r["n"], pct(r["en"])]
        for lang in langs:
            if lang not in r["langs"]:
                cells.append("–")
                continue
            acc, ci = r["langs"][lang]
            delta = f"{100 * (acc - r['en']):+.1f}"
            cells.append(f"{pct(acc)} ({delta}" + (f", {100 * ci[0]:+.1f} to {100 * ci[1]:+.1f})" if ci else ")"))
        main_rows.append(cells)

    mean_cells = ["mean over models", "", pct(statistics.fmean(r["en"] for r in rows))]
    for lang in langs:
        have = [r for r in rows if lang in r["langs"]]
        if not have:
            mean_cells.append("–")
            continue
        a = statistics.fmean(r["langs"][lang][0] for r in have)
        e = statistics.fmean(r["en"] for r in have)
        mean_cells.append(f"{pct(a)} ({100 * (a - e):+.1f})")
    main_rows.append(mean_cells)

    slice_rows = [[k, pct(statistics.fmean(slice_acc[k]["en"]))] +
                  [pct(statistics.fmean(slice_acc[k][lang])) if slice_acc[k][lang] else "–" for lang in langs]
                  for k in SLICES if slice_acc[k]["en"]]

    title = "state and question translated" if args.variant == "full" else "state translated, question in English"
    out = [
        f"# Decision models in other languages ({title})",
        "",
        f"Accuracy (%) over {len(SLICES)} slices, each weighted equally. In brackets: change from",
        "English in points" + ("" if args.no_ci else ", then its paired bootstrap 95% interval") + ".",
        "Each model is scored on the cases that its English run and all its translated runs answered.",
        "",
        C.table(main_rows, head),
        "",
        "## By slice (mean over models)",
        "",
        C.table(slice_rows, ["slice", "English"] + [LANG_NAMES.get(lang, lang) for lang in langs]),
        "",
        "## Coverage",
        "",
        C.table(coverage, ["model", "language", "answered", "paired"]),
        "",
    ]
    text = "\n".join(out)
    print(text)
    path = C.REPORTS / f"MULTILINGUAL{'' if args.variant == 'full' else '_enq'}.md"
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(C.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
