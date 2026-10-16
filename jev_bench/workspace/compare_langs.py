"""English versus translated runs of the OpenRouter decision models.

    uv run workspace/compare_langs.py
    uv run workspace/compare_langs.py --langs zh ar hi vi --variant state

Reads predictions only, no model calls. English is each model's run_id in
models.json; a translated run is <label>-<lang> (state and question translated)
or <label>-<lang>-enq (state translated, question in English), as written by
scripts/45_run_multilingual.sh.

Each language is paired with English on its own: a model's change in a language
is computed on the cases both its English run and that language's run answered
without error. Cases the translator did not deliver are absent from the
translated sets, so this keeps English from being scored on extra items, and one
unfinished language cannot shrink the cases behind the others.

A translated run counts only once it has answered at least --min-coverage of
the cases in its case files. Runs still going, or cut short (for example by an
HTTP 402 when OpenRouter credits ran out), are listed under "Not included".

The headline is the mean accuracy over the chosen slices (default: the five
safety slices), each slice weighted equally. The 95% interval on a change is a
paired bootstrap over families; a change is bold when its interval excludes 0.
Means over models use only the models finished in every language listed, so
every column averages the same models.

Writes ../local_notes/MULTILINGUAL.md (or MULTILINGUAL_enq.md for --variant state);
local_notes/ is gitignored.
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
SHORT = {"jailbreak_classification": "Jailbreak", "prompt_injections": "Prompt injection", "aegis2": "Harmful prompt (Aegis)",
         "aegis2_response": "Harmful response (Aegis)", "atbench500": "Agent safety (ATBench)"}
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


def md_table(rows: list[list], headers: list[str], align: str = "") -> str:
    """Markdown pipe table. align: one letter per column, l or r (default: first l, rest r)."""
    align = align or "l" + "r" * (len(headers) - 1)
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(":---" if a == "l" else "---:" for a in align) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def expected_cases(lang: str, suffix: str) -> int:
    folder = C.DATA / (f"cases_{lang}" if suffix else f"cases_{lang}_full")
    return sum(sum(1 for _ in C.read_jsonl(folder / f"{k}.jsonl")) for k in SLICES if (folder / f"{k}.jsonl").exists())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--langs", nargs="+", default=["zh", "ar", "hi", "vi", "sw", "es", "ta", "kn", "fr", "ru"])
    ap.add_argument("--variant", choices=["full", "state"], default="full")
    ap.add_argument("--slices", nargs="+", default=SLICES, help="default: the five safety slices")
    ap.add_argument("--min-coverage", type=float, default=0.97,
                    help="a run counts once it answered this share of its language's cases")
    ap.add_argument("--no-ci", action="store_true", help="skip the bootstrap, faster")
    args = ap.parse_args()
    SLICES[:] = args.slices
    suffix = "" if args.variant == "full" else "-enq"

    models = json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]
    models = [m for m in models if m.get("endpoint") == "openrouter" and (C.RUNS / m["run_id"]).exists()]
    expected = {lang: expected_cases(lang, suffix) for lang in args.langs}

    # results[model][lang] = (accuracy, english accuracy on the same cases, ci, by_slice, english by_slice, cases)
    results: dict[str, dict[str, tuple]] = {}
    en_full: dict[str, float] = {}
    skipped: list[list] = []
    for m in models:
        en = load(m["run_id"])
        if not en:
            continue
        en_full[m["name"]] = macro(en, sorted(en))[0]
        results[m["name"]] = {}
        for lang in args.langs:
            run_id = f"{m['label']}-{lang}{suffix}"
            recs = load(run_id)
            need = expected[lang]
            if not need:
                continue
            if len(recs) < args.min_coverage * need:
                state = "not started" if not (C.RUNS / run_id).exists() else "running or cut short"
                skipped.append([m["name"], LANG_NAMES[lang], f"{len(recs):,} / {need:,}", state])
                continue
            ids = sorted(set(en) & set(recs))
            acc, by_slice = macro(recs, ids)
            en_acc, en_slices = macro(en, ids)
            ci = None if args.no_ci else paired_ci(en, recs, ids)
            results[m["name"]][lang] = (acc, en_acc, ci, by_slice, en_slices, len(ids))
        print(f"  {m['name']}: {', '.join(results[m['name']]) or 'no finished language'}", flush=True)

    langs = [lang for lang in args.langs if any(lang in r for r in results.values())]
    if not langs:
        print(f"No finished translated runs (variant {args.variant}). Run scripts/45_run_multilingual.sh first.")
        return 2
    names = sorted((n for n in results if results[n]), key=lambda n: -en_full[n])
    complete = [n for n in names if all(lang in results[n] for lang in langs)]
    heads = [LANG_NAMES[lang] for lang in langs]

    # 1. change from English, the headline
    delta_rows = []
    for n in names:
        cells = [n]
        for lang in langs:
            if lang not in results[n]:
                cells.append("·")
                continue
            acc, en_acc, ci, *_ = results[n][lang]
            d = f"{100 * (acc - en_acc):+.1f}".replace("-", "−")
            significant = ci and (ci[0] > 0 or ci[1] < 0)
            cells.append(f"**{d}**" if significant else d)
        delta_rows.append(cells)
    if complete:
        cells = [f"*mean, {len(complete)} models*"]
        for lang in langs:
            d = statistics.fmean(results[n][lang][0] - results[n][lang][1] for n in complete)
            cells.append(f"*{100 * d:+.1f}*".replace("-", "−"))
        delta_rows.append(cells)

    # 2. accuracy
    acc_rows = []
    for n in names:
        acc_rows.append([n, pct(en_full[n])] + [pct(results[n][lang][0]) if lang in results[n] else "·" for lang in langs])
    if complete:
        acc_rows.append([f"*mean, {len(complete)} models*", f"*{pct(statistics.fmean(en_full[n] for n in complete))}*"] +
                        [f"*{pct(statistics.fmean(results[n][lang][0] for n in complete))}*" for lang in langs])

    # 3. by slice, over the models finished in every language
    slice_rows = []
    pool = complete or names
    for k in SLICES:
        en_vals = [results[n][lang][4][k] for n in pool for lang in langs if lang in results[n] and k in results[n][lang][4]]
        if not en_vals:
            continue
        cells = [SHORT.get(k, k), pct(statistics.fmean(en_vals))]
        for lang in langs:
            vals = [results[n][lang][3][k] for n in pool if lang in results[n] and k in results[n][lang][3]]
            cells.append(pct(statistics.fmean(vals)) if vals else "·")
        slice_rows.append(cells)

    # 4. intervals and cases, for checking
    ci_rows = []
    for n in names:
        for lang in langs:
            if lang not in results[n]:
                continue
            acc, en_acc, ci, _, _, k = results[n][lang]
            ci_rows.append([n, LANG_NAMES[lang], k, pct(en_acc), pct(acc), f"{100 * (acc - en_acc):+.1f}",
                            f"{100 * ci[0]:+.1f} to {100 * ci[1]:+.1f}" if ci else "–"])

    title = "state and question translated" if args.variant == "full" else "state translated, question in English"
    pool_note = (f"the {len(complete)} models finished in every language shown" if complete
                 else "every model with a finished run in that language (no model is finished in all of them yet)")
    out = [
        f"# Decision models in other languages ({title})",
        "",
        f"{len(SLICES)} safety benchmarks: " + ", ".join(SHORT.get(k, k) for k in SLICES) + ". "
        "Accuracy is the mean over these benchmarks, each weighted equally, with the yes/no cut at p = 0.5.",
        "",
        f"Models with a finished run: {len(names)}. Finished in every language shown: {len(complete)}. "
        "`·` means that run is not finished yet.",
        "",
        "## Change from English (points)",
        "",
        "Each cell compares the model with its own English answers on the same cases. "
        "**Bold**: the 95% interval excludes 0, so the change is not noise." if not args.no_ci else
        "Each cell compares the model with its own English answers on the same cases.",
        "",
        md_table(delta_rows, ["Model"] + heads),
        "",
        "## Accuracy (%)",
        "",
        "English is on all its cases; a language is on the cases it shares with English.",
        "",
        md_table(acc_rows, ["Model", "English"] + heads),
        "",
        "## By benchmark (accuracy %, mean over models)",
        "",
        f"Averaged over {pool_note}.",
        "",
        md_table(slice_rows, ["Benchmark", "English"] + heads),
        "",
    ]
    if skipped:
        out += ["## Not included yet", "",
                f"Runs with fewer than {args.min_coverage:.0%} of their cases answered.", "",
                md_table(skipped, ["Model", "Language", "Answered", "State"], "llrl"), ""]
    out += ["## Detail: cases and 95% intervals", "",
            md_table(ci_rows, ["Model", "Language", "Cases", "English", "Language acc.", "Change", "95% interval"], "llrrrrr"), ""]
    text = "\n".join(out)
    path = C.ROOT.parent / "local_notes" / f"MULTILINGUAL{'' if args.variant == 'full' else '_enq'}.md"
    path.write_text(text, encoding="utf-8")
    print()
    print(C.table([[r[0].strip("*")] + [str(c).strip("*") for c in r[1:]] for r in delta_rows], ["change from English"] + heads))
    if skipped:
        print(f"\n{len(skipped)} runs not finished yet; see the report.")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
