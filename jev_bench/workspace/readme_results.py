"""Write the README's results and models tables from the scored runs.

    uv run workspace/readme_results.py

Replaces everything between <!-- results:start --> and <!-- results:end --> in
../README.md. Every number comes from data/runs/<run_id>/scores.json; rerun after
scoring to refresh. Datasets are rows, grouped by area; models are columns.
"""

from __future__ import annotations

import json
import re
import time

import common as C
from build_site import DATASETS
from jevbench_index import CLUSTERS, MERGE, index_for, slice_info, unsupported_keys

README = C.ROOT.parent / "README.md"
START, END = "<!-- results:start -->", "<!-- results:end -->"
MODELS_START, MODELS_END = "<!-- models:start -->", "<!-- models:end -->"
GROUPS = ["Safety", "Medicine", "Exams", "Language", "Tools", "Ranking", "Judging", "Images"]
PCT = {"accuracy", "server_routing_accuracy", "tool_selection_accuracy"}
SHORT = {
    "Jev 1.13": "Jev 1.13", "djev-0.1": "djev", "Laya 421M": "Laya",
    "Clef": "Clef", "Clef-flash": "Clef-flash", "Clef-omni": "Clef-omni", "pplx-decider v1.1": "pplx v1.1",
    "GPT-6 Luna Decisions": "GPT-6 Luna", "Microsoft Decision 1": "MS Decision 1", "Solar Decide": "Solar",
    "Solar Decide Flash": "Solar Flash", "Drex v1.5": "Drex", "Mercury Decide": "Mercury",
    "TEv1 4B (exp.)": "TEv1 4B", "Kev 4B": "Kev 4B", "Span-01": "Span-01",
    "Liquid d1-3B (local)": "d1-3B", "Liquid d1-omni-600M (local)": "d1-omni",
}


def load_slices(run_id: str, also: list[str]) -> dict:
    out: dict = {}
    for r in [*also, run_id]:
        p = C.RUNS / r / "scores.json"
        if p.exists():
            out.update(json.loads(p.read_text(encoding="utf-8"))["slices"])
    return out


def cell(entry: dict | None, key: str) -> tuple[float | None, str]:
    """(comparable value, display text) for one model on one dataset."""
    if not entry or not entry.get("headline"):
        return None, "–"
    if key == "helpsteer2_helpfulness":
        sp = (entry.get("metrics") or {}).get("spearman_expected_level")
        return (sp, f"{sp:.3f}") if sp is not None else (None, "–")
    h = entry["headline"]
    v = h["value"]
    text = f"{v * 100:.1f}" if h["metric"] in PCT else f"{v:.2f}" if h["metric"] == "mae_expected_level" else f"{v:.3f}"
    if entry.get("coverage", 1) < 0.995:
        text += "*"
    return (-v if h["metric"] == "mae_expected_level" else v), text


def main() -> int:
    models = json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]
    by_name = {m["name"]: m for m in models}
    merged_away = set(MERGE.values())
    scores = {m["name"]: load_slices(m["run_id"], m.get("also_read", [])) for m in models}
    keys = [k for k in C.available_case_keys() if k in DATASETS]

    columns = []
    for m in models:
        if m["name"] in merged_away:
            continue
        row = dict(scores[m["name"]])
        filled = set()
        if m["name"] in MERGE:
            for k, v in scores[MERGE[m["name"]]].items():
                if k not in row or not row[k].get("headline"):
                    row[k] = v
                    filled.add(k)
        if any(k in row and row[k].get("headline") for k in keys):
            columns.append((m, row, filled))

    def label(key: str) -> str:
        name, group, url, _ = DATASETS[key]
        if group == "Ranking":
            bm25 = next((r[key]["ranking"]["bm25_ndcg@10"] for _, r, _ in columns if r.get(key, {}).get("ranking")), None)
            return f"[{name}]({url}) (BM25 {bm25:.3f})" if bm25 is not None else f"[{name}]({url})"
        suffix = {"helpsteer2_helpfulness": ", Spearman", "sst5": ", MAE ↓"}.get(key, "")
        return f"[{name}]({url}){suffix}"

    head = "| Dataset | n | " + " | ".join(SHORT.get(m["name"], m["name"]) for m, _, _ in columns) + " |"
    sep = "|---|---:|" + "---:|" * len(columns)
    lines = [head, sep]
    for group in GROUPS:
        gkeys = [k for k in keys if DATASETS[k][1] == group and any(r.get(k, {}).get("headline") for _, r, _ in columns)]
        if not gkeys:
            continue
        lines.append(f"| **{group}** |" + " |" * (len(columns) + 1))
        for k in gkeys:
            vals = [cell(r.get(k), k) for _, r, _ in columns]
            best = max((v for v, _ in vals if v is not None), default=None)
            n = next((r[k]["n_cases"] for _, r, _ in columns if r.get(k, {}).get("n_cases")), "")
            texts = []
            for (v, t), (_, _, filled) in zip(vals, columns):
                if k in filled and t != "–":
                    t += "†"
                texts.append(f"**{t}**" if v is not None and v == best else t)
            lines.append(f"| {label(k)} | {n:,} | " + " | ".join(texts) + " |")

    info = slice_info(C.read_cases, {k for ks in CLUSTERS.values() for k in ks})
    ranked = []
    for m, r, _ in columns:
        ix = index_for(r, unsupported_keys(m, info))
        ranked.append((m["name"].replace(" (hosted)", ""), ix))
    ranked.sort(key=lambda t: (t[1]["index"] is None, -(t[1]["index"] or 0)))
    index_rows = ["| # | Model | **Index** | " + " | ".join(CLUSTERS) + " |", "|---:|---|---:|" + "---:|" * len(CLUSTERS)]
    for place, (name, ix) in enumerate(ranked, 1):
        cl = " | ".join("–" if v is None else f"{v:.1f}" for v in ix["clusters"].values())
        if ix["index"] is None:
            head = "–"
        else:
            head = f"**{ix['index']:.1f}**" + ("‡" if ix["zeroed"] else "")
            if ix["clusters_counted"] < len(CLUSTERS):
                head += f" ({ix['clusters_counted']}/{len(CLUSTERS)})"
            elif not ix["complete"]:
                head += "*"
        index_rows.append(f"| {place} | {name} | {head} | {cl} |")

    order = ["Hugging Face", "Website", "Code", "Runbook"]
    model_rows = ["| Model | Runs on | Architecture | Licence | Links |", "|---|---|---|---|---|"]
    for m, _, _ in columns:
        links = sorted((m.get("links") or {}).items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 9)
        kind = "Open weights" if "Hugging Face" in dict(links) else m.get("hosting", "API")
        model_rows.append(f"| {m['name']} | {kind} | {m.get('architecture') or '–'} | {m.get('licence') or 'not checked'} | " + " · ".join(f"[{k}]({u})" for k, u in links) + " |")

    block = "\n".join([
        START,
        "### JevBench Index",
        "",
        "One number per model: every dataset on 0-100, averaged within six clusters, then the six "
        "clusters averaged. Datasets not run yet are left out: (4/6) means the score covers four of the six "
        "clusters, and * that a cluster is missing a dataset. ‡ the model's API rejects some datasets outright "
        "(too many options, or question types it does not take); those count as 0.",
        "",
        *index_rows,
        "",
        "### Every dataset",
        "",
        f"Every model on every dataset, from the scored runs on {time.strftime('%Y-%m-%d')}. Accuracy in %, "
        "except where the row says otherwise; ranking rows are nDCG@10 on a fixed BM25 top-20, with BM25's own "
        "score in the label. Bold is the best on each row.",
        "",
        *lines,
        "",
        "– not run, or not supported by that API (option limits, question types, no image input). "
        "\\* under 99.5% of cases answered, from refusals or errors. "
        "† Liquid D1 on the newer datasets, run through a second API route to the same hosted model.",
        "",
        "Explore every cell, with intervals and examples, on the [website](https://leanmcp.github.io/jevbench/). "
        "Where each model runs: [Models](#models).",
        END,
    ])
    models_block = "\n".join([MODELS_START, *model_rows, MODELS_END])
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"README.md has no {START} ... {END} block")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    # The models table lives at the very end of the README, in its own block.
    if MODELS_START in text:
        text = re.sub(re.escape(MODELS_START) + r".*?" + re.escape(MODELS_END), lambda _: models_block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n## Models\n\n" + models_block + "\n"
    README.write_text(text, encoding="utf-8")
    print(f"wrote {len(lines) - 2} rows x {len(columns)} models into README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
