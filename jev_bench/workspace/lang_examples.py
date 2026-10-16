"""Cases where the models agree in English and fall apart in a translation, or the reverse.

    uv run workspace/lang_examples.py
    uv run workspace/lang_examples.py --langs zh ar --n 6 --chars 400

For every case answered by every model in English and in each language, counts
how many of the OpenRouter models got it right per language, then prints the
cases with the largest swing, with the English text and the translated text
side by side. Reads predictions and case files only, no model calls.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

import common as C
from compare_langs import LANG_NAMES, SLICES
from score_runs import is_correct


def state_text(case: dict, limit: int) -> str:
    state = case["state"]
    text = "\n".join(f"[{k}] {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}" for k, v in state.items()) \
        if isinstance(state, dict) else str(state)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " …"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--langs", nargs="+", default=["zh", "ar"])
    ap.add_argument("--n", type=int, default=5, help="examples per language and direction")
    ap.add_argument("--chars", type=int, default=350, help="characters of text shown per case")
    args = ap.parse_args()

    models = [m for m in json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]
              if m.get("endpoint") == "openrouter"]
    langs = ["en"] + args.langs
    right: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))  # lang -> case -> models right
    seen: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    used = []
    for m in models:
        runs = {lang: (m["run_id"] if lang == "en" else f"{m['label']}-{lang}") for lang in langs}
        if not all((C.RUNS / r / "predictions.jsonl").exists() for r in runs.values()):
            continue
        used.append(m["name"])
        for lang, run in runs.items():
            for r in C.read_jsonl(C.RUNS / run / "predictions.jsonl"):
                if r["slice"] not in SLICES or r.get("error") or r.get("answer_type") != r["task_type"]:
                    continue
                seen[lang][r["case_id"]].add(m["name"])
                if is_correct(r, r["task_type"]):
                    right[lang][r["case_id"]].append(m["name"])
    n_models = len(used)
    ids = [cid for cid in seen["en"] if all(len(seen[lang][cid]) == n_models for lang in langs)]
    print(f"{n_models} models, {len(ids):,} cases answered by all of them in {', '.join(LANG_NAMES[l] for l in langs)}\n")

    cases = {lang: {} for lang in langs}
    for lang in langs:
        folder = C.DATA / ("cases" if lang == "en" else f"cases_{lang}_full")
        for key in SLICES:
            path = folder / f"{key}.jsonl"
            if path.exists():
                cases[lang].update({c["case_id"]: c for c in C.read_jsonl(path)})

    def show(cid: str, lang: str) -> None:
        en_case = cases["en"][cid]
        counts = "  ".join(f"{LANG_NAMES[l]} {len(right[l][cid])}/{n_models}" for l in langs)
        lost = sorted(set(right["en"][cid]) - set(right[lang][cid]))
        gained = sorted(set(right[lang][cid]) - set(right["en"][cid]))
        print(f"--- {cid}   slice {en_case['slice']}   gold {en_case['gold']}")
        print(f"    right: {counts}")
        if lost:
            print(f"    wrong only in {LANG_NAMES[lang]}: {', '.join(lost)}")
        if gained:
            print(f"    right only in {LANG_NAMES[lang]}: {', '.join(gained)}")
        print(f"    EN: {state_text(en_case, args.chars)}")
        print(f"    {lang.upper()}: {state_text(cases[lang][cid], args.chars)}\n")

    for lang in args.langs:
        swing = sorted(ids, key=lambda c: len(right[lang][c]) - len(right["en"][c]))
        print(f"=============== {LANG_NAMES[lang]}: right in English, wrong in {LANG_NAMES[lang]}\n")
        for cid in swing[: args.n]:
            show(cid, lang)
        print(f"=============== {LANG_NAMES[lang]}: wrong in English, right in {LANG_NAMES[lang]}\n")
        for cid in reversed(swing[-args.n:]):
            show(cid, lang)

    # Per slice and gold label: where the drop sits.
    print("=============== models right, mean per case, by slice and gold label\n")
    rows = []
    groups = defaultdict(list)
    for cid in ids:
        c = cases["en"][cid]
        groups[(c["slice"], str(c["gold"]))].append(cid)
    for (key, gold), group in sorted(groups.items()):
        rows.append([key, gold, len(group)] + [f"{sum(len(right[l][c]) for c in group) / len(group):.1f}" for l in langs])
    print(C.table(rows, ["slice", "gold", "cases"] + [LANG_NAMES[l] for l in langs]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
