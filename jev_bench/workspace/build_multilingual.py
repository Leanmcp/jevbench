"""Every multilingual number in one place: the website page and the paper tables.

    uv run workspace/build_multilingual.py

Reads predictions only, no model calls. For each OpenRouter model and each
language it pairs the translated run (<label>-<lang>, state and question
translated) with the model's own English run on the cases both answered, as
compare_langs.py does, and adds per-slice AUROC and how often the model says
yes, which separate a moved threshold from a loss of skill.

Writes:
  ../site/multilingual-data.js        window.JEVBENCH_ML, read by site/multilingual.html
  data/multilingual/summary.json      the same numbers, for paper_tables_multilingual.py

A translated run counts once it has answered at least 97% of its cases; runs
still going are listed as pending, never scored.
"""

from __future__ import annotations

import collections
import json
import statistics
import time

import common as C
from build_site import CITATION, clip
from compare_langs import SLICES, expected_cases, load, macro, paired_ci
from score_runs import auroc, is_correct

SITE = C.ROOT.parent / "site"
OUT = C.DATA / "multilingual"
MIN_COVERAGE = 0.97
EXAMPLES_PER_DIRECTION = 10
TEXT_LIMIT = 900

# code: (English name, native name, family, script)
LANGS = {
    "zh": ("Chinese", "中文", "Sino-Tibetan", "Han (Simplified)"),
    "ar": ("Arabic", "العربية", "Afro-Asiatic, Semitic", "Arabic"),
    "hi": ("Hindi", "हिन्दी", "Indo-European, Indo-Aryan", "Devanagari"),
    "vi": ("Vietnamese", "Tiếng Việt", "Austroasiatic", "Latin"),
    "sw": ("Swahili", "Kiswahili", "Niger-Congo, Bantu", "Latin"),
    "es": ("Spanish", "Español", "Indo-European, Romance", "Latin"),
    "fr": ("French", "Français", "Indo-European, Romance", "Latin"),
    "ru": ("Russian", "Русский", "Indo-European, Slavic", "Cyrillic"),
}
SLICE_NAMES = {"jailbreak_classification": "Jailbreak", "prompt_injections": "Prompt injection",
               "aegis2": "Aegis 2.0 prompts", "aegis2_response": "Aegis 2.0 responses", "atbench500": "ATBench"}


def rate(values) -> float | None:
    values = list(values)
    return statistics.fmean(values) if values else None


def slice_stats(recs: dict, ids: list[str]) -> dict:
    out = {}
    by = collections.defaultdict(list)
    for cid in ids:
        by[recs[cid]["slice"]].append(recs[cid])
    for key, rs in by.items():
        out[key] = {"n": len(rs),
                    "acc": rate(is_correct(r, r["task_type"]) for r in rs),
                    "auroc": auroc([float(r["p_true"]) for r in rs], [bool(r["gold"]) for r in rs]),
                    "yes": rate(float(r["p_true"]) >= 0.5 for r in rs),
                    "gold_yes": rate(bool(r["gold"]) for r in rs)}
    return out


def macro_auroc(stats: dict) -> float | None:
    vals = [s["auroc"] for s in stats.values() if s["auroc"] is not None]
    return statistics.fmean(vals) if vals else None


def state_text(case: dict) -> str | dict:
    """The state as the page shows it: a dict of fields, each clipped and redacted."""
    st = clip(case["state"], TEXT_LIMIT)
    return st if isinstance(st, dict) else {"state": st}


def r4(x):
    return None if x is None else round(x, 4)


def main() -> int:
    models = [m for m in json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]
              if m.get("endpoint") == "openrouter" and (C.RUNS / m["run_id"]).exists()
              and any((C.RUNS / f"{m['label']}-{lang}").exists() for lang in LANGS)]
    expected = {lang: expected_cases(lang, "") for lang in LANGS}

    en_recs = {m["name"]: load(m["run_id"]) for m in models}
    lang_recs: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    status: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    for m in models:
        for lang in LANGS:
            recs = load(f"{m['label']}-{lang}")
            need = expected[lang]
            done = need and len(recs) >= MIN_COVERAGE * need
            status[m["name"]][lang] = {"answered": len(recs), "cases": need, "complete": bool(done)}
            if done:
                lang_recs[m["name"]][lang] = recs

    # English on all its safety cases, per model.
    english = {}
    for m in models:
        ids = sorted(en_recs[m["name"]])
        acc, _ = macro(en_recs[m["name"]], ids)
        st = slice_stats(en_recs[m["name"]], ids)
        english[m["name"]] = {"n": len(ids), "acc": r4(acc), "auroc": r4(macro_auroc(st)),
                              "slices": {k: {kk: r4(vv) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in st.items()}}

    results: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    for m in models:
        name = m["name"]
        for lang, recs in lang_recs[name].items():
            en = en_recs[name]
            ids = sorted(set(en) & set(recs))
            acc, _ = macro(recs, ids)
            en_acc, _ = macro(en, ids)
            ci = paired_ci(en, recs, ids)
            st_xx, st_en = slice_stats(recs, ids), slice_stats(en, ids)
            results[name][lang] = {
                "n": len(ids), "acc": r4(acc), "en_acc": r4(en_acc), "delta": r4(acc - en_acc),
                "ci": [r4(ci[0]), r4(ci[1])], "significant": ci[0] > 0 or ci[1] < 0,
                "auroc": r4(macro_auroc(st_xx)), "en_auroc": r4(macro_auroc(st_en)),
                "slices": {k: {"n": st_xx[k]["n"], "acc": r4(st_xx[k]["acc"]), "en_acc": r4(st_en[k]["acc"]),
                               "auroc": r4(st_xx[k]["auroc"]), "en_auroc": r4(st_en[k]["auroc"]),
                               "yes": r4(st_xx[k]["yes"]), "en_yes": r4(st_en[k]["yes"]),
                               "gold_yes": r4(st_xx[k]["gold_yes"])} for k in st_xx},
            }
        print(f"  {name}: {', '.join(results[name]) or 'no finished language'}", flush=True)

    names = [m["name"] for m in models]
    complete_all = [n for n in names if all(lang in results[n] for lang in LANGS)]

    def mean_over(pool, lang, field, sl=None):
        vals = [(results[n][lang]["slices"][sl] if sl else results[n][lang])[field] for n in pool
                if lang in results[n] and (not sl or sl in results[n][lang]["slices"])]
        vals = [v for v in vals if v is not None]
        return r4(statistics.fmean(vals)) if vals else None

    languages = []
    for lang, (name, native, family, script) in LANGS.items():
        have = [n for n in names if lang in results[n]]
        languages.append({
            "code": lang, "name": name, "native": native, "family": family, "script": script,
            "models_complete": len(have), "models_total": len(names),
            "acc": mean_over(have, lang, "acc"), "en_acc": mean_over(have, lang, "en_acc"),
            "delta": mean_over(have, lang, "delta"), "auroc": mean_over(have, lang, "auroc"),
            "en_auroc": mean_over(have, lang, "en_auroc"),
            "common": {"acc": mean_over(complete_all, lang, "acc"), "en_acc": mean_over(complete_all, lang, "en_acc"),
                       "delta": mean_over(complete_all, lang, "delta")} if complete_all else None,
            "slices": {k: {"acc": mean_over(have, lang, "acc", k), "en_acc": mean_over(have, lang, "en_acc", k),
                           "auroc": mean_over(have, lang, "auroc", k), "en_auroc": mean_over(have, lang, "en_auroc", k)}
                       for k in SLICES},
            "slices_common": {k: {"acc": mean_over(complete_all, lang, "acc", k), "en_acc": mean_over(complete_all, lang, "en_acc", k)}
                              for k in SLICES} if complete_all else None,
        })

    # Translation coverage: cases in each translated slice against English.
    english_cases = {k: C.read_cases(k) for k in SLICES}
    translation = {}
    for lang in LANGS:
        folder = C.DATA / f"cases_{lang}_full"
        translation[lang] = {k: {"cases": len(english_cases[k]),
                                 "usable": sum(1 for _ in C.read_jsonl(folder / f"{k}.jsonl")) if (folder / f"{k}.jsonl").exists() else 0}
                             for k in SLICES}
        rows = list(C.read_jsonl(C.DATA / "translations" / lang / "translations.jsonl"))
        translation[lang]["_segments"] = {"records": len(rows),
                                          "translator": sorted({r.get("model") for r in rows if r.get("model")}),
                                          "reasoning_effort": sorted({r.get("reasoning_effort") for r in rows if r.get("reasoning_effort")})}

    # Examples: per language, the cases with the largest swing in models right,
    # over the models finished in that language.
    examples = {}
    for lang in LANGS:
        pool = [n for n in names if lang in results[n]]
        if not pool:
            examples[lang] = []
            continue
        xx_cases = {}
        folder = C.DATA / f"cases_{lang}_full"
        for k in SLICES:
            if (folder / f"{k}.jsonl").exists():
                xx_cases.update({c["case_id"]: c for c in C.read_jsonl(folder / f"{k}.jsonl")})
        en_cases = {c["case_id"]: c for k in SLICES for c in english_cases[k]}
        ids = [cid for cid in xx_cases if cid in en_cases
               and all(cid in en_recs[n] and cid in lang_recs[n][lang] for n in pool)]
        right = {cid: (sum(is_correct(en_recs[n][cid], "noul") for n in pool),
                       sum(is_correct(lang_recs[n][lang][cid], "noul") for n in pool)) for cid in ids}
        order = sorted(ids, key=lambda c: (right[c][1] - right[c][0], c))
        picked = [(c, "worse") for c in order[:EXAMPLES_PER_DIRECTION]] + \
                 [(c, "better") for c in reversed(order[-EXAMPLES_PER_DIRECTION:])]
        rows = []
        for cid, direction in picked:
            en_c, xx_c = en_cases[cid], xx_cases[cid]
            rows.append({
                "case_id": cid, "slice": en_c["slice"], "gold": bool(en_c["gold"]), "direction": direction,
                "right_en": right[cid][0], "right_xx": right[cid][1], "models": len(pool),
                "question_en": en_c["question"]["instructions"].replace(C.UNTRUSTED_PREFIX, "").strip(),
                "question_xx": xx_c["question"]["instructions"],
                "state_en": state_text(en_c), "state_xx": state_text(xx_c),
                "answers": {n: {"en": round(float(en_recs[n][cid]["p_true"]), 4),
                                "xx": round(float(lang_recs[n][lang][cid]["p_true"]), 4)} for n in pool},
            })
        examples[lang] = rows

    payload = {
        "generated": time.strftime("%Y-%m-%d"), "min_coverage": MIN_COVERAGE, "citation": CITATION,
        "slices": [{"key": k, "name": SLICE_NAMES[k]} for k in SLICES],
        "languages": languages, "models": names, "complete_all": complete_all,
        "english": english, "results": results, "status": status,
        "translation": translation, "examples": examples,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    site_payload = {k: v for k, v in payload.items()}
    (SITE / "multilingual-data.js").write_text(
        "window.JEVBENCH_ML = " + json.dumps(site_payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    pending = sum(1 for n in names for lang in LANGS if not status[n][lang]["complete"])
    print(f"\n{len(names)} models, {len(LANGS)} languages, {len(complete_all)} models finished in every language, "
          f"{pending} runs pending")
    for lg in languages:
        print(f"  {lg['name']:<10} {lg['models_complete']:>2}/{lg['models_total']} models  "
              f"acc {100 * (lg['acc'] or 0):5.1f}  vs English {100 * (lg['delta'] or 0):+5.1f}")
    print(f"wrote {OUT / 'summary.json'} and {SITE / 'multilingual-data.js'} "
          f"({(SITE / 'multilingual-data.js').stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
