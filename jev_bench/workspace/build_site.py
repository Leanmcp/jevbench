"""Build the static JevBench website data from the scored runs.

    uv run workspace/build_site.py

Writes ../site/data.js (results, ranking detail, ten examples per dataset with
every model's answer) and copies the example images. The page itself is the
hand-written site/index.html, site/app.js and site/style.css; open
site/index.html directly or serve the folder from GitHub Pages.

Text from sources whose licence does not allow redistribution (SST-5,
MCP-Bench) is withheld; their examples show the answer and the model
decisions only.
"""

from __future__ import annotations

import json
import re
import shutil
import time

import common as C
from jevbench_index import CLUSTERS, MERGE, index_for, slice_info, to_100, unsupported_keys

SITE = C.ROOT.parent / "site"
EXAMPLES_PER_DATASET = 10
TEXT_CLIP = 1500
DOC_CLIP = 320

PAPER = {
    "page": "https://www.preprints.org/manuscript/202610.0181",
    "pdf": "https://www.preprints.org/frontend/manuscript/da3d1f1f93bf32fe4a28e70c6168ef87/download_pub",
    "dataset": "https://huggingface.co/datasets/Leanmcp/jevbench",
    "github": "https://github.com/Leanmcp/jevbench",
}
CITATION = """@misc{pai2026jevbench,
  title        = {{JevBench}: An Open Evaluation Framework for Typed Decision Models},
  author       = {Pai, Dheeraj Mohandas and Xian, Lu},
  year         = {2026},
  howpublished = {Preprints.org},
  url          = {https://www.preprints.org/manuscript/202610.0181}
}"""

# key: (display name, group, Hugging Face or source URL, adversarial text)
DATASETS = {
    "aegis2": ("Aegis 2.0 prompts", "Safety", "https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-2.0", True),
    "aegis2_response": ("Aegis 2.0 responses", "Safety", "https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-2.0", True),
    "atbench500": ("ATBench", "Safety", "https://huggingface.co/datasets/AI45Research/ATBench", True),
    "jailbreak_classification": ("Jailbreak classification", "Safety", "https://huggingface.co/datasets/jackhhao/jailbreak-classification", True),
    "prompt_injections": ("Prompt injections", "Safety", "https://huggingface.co/datasets/deepset/prompt-injections", True),
    "medmcqa": ("MedMCQA", "Medicine", "https://huggingface.co/datasets/openlifescienceai/medmcqa", False),
    "medqa_usmle": ("MedQA-USMLE", "Medicine", "https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options", False),
    "pubmedqa": ("PubMedQA", "Medicine", "https://huggingface.co/datasets/qiaojin/PubMedQA", False),
    "mmlu_pro": ("MMLU-Pro", "Exams", "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro", False),
    "scienceqa_text": ("ScienceQA", "Exams", "https://huggingface.co/datasets/derek-thomas/ScienceQA", False),
    "scienceqa_image": ("ScienceQA images", "Images", "https://huggingface.co/datasets/derek-thomas/ScienceQA", False),
    "vqa_rad": ("VQA-RAD", "Images", "https://huggingface.co/datasets/flaviagiammarino/vqa-rad", False),
    "banking77": ("BANKING77", "Language", "https://huggingface.co/datasets/mteb/banking77", False),
    "sst5": ("SST-5", "Language", "https://huggingface.co/datasets/SetFit/sst5", False),
    "mcpbench_server_routing": ("MCP-Bench routing", "Tools", "https://github.com/Accenture/mcp-bench", False),
    "mcpbench_tool_selection": ("MCP-Bench tools", "Tools", "https://github.com/Accenture/mcp-bench", False),
    "mcpmark_server_routing": ("MCPMark routing", "Tools", "https://github.com/eval-sys/mcpmark", False),
    "mcpmark_tool_selection": ("MCPMark tools", "Tools", "https://github.com/eval-sys/mcpmark", False),
    "scifact_rank_noul": ("SciFact, per document", "Ranking", "https://huggingface.co/datasets/BeIR/scifact", False),
    "scifact_rank_choice": ("SciFact, all at once", "Ranking", "https://huggingface.co/datasets/BeIR/scifact", False),
    "nfcorpus_rank_noul": ("NFCorpus, per document", "Ranking", "https://huggingface.co/datasets/BeIR/nfcorpus", False),
    "nfcorpus_rank_choice": ("NFCorpus, all at once", "Ranking", "https://huggingface.co/datasets/BeIR/nfcorpus", False),
    "nfcorpus_rank_graded": ("NFCorpus, graded", "Ranking", "https://huggingface.co/datasets/BeIR/nfcorpus", False),
    "helpsteer2_helpfulness": ("HelpSteer2", "Judging", "https://huggingface.co/datasets/nvidia/HelpSteer2", False),
    "rewardbench2": ("RewardBench 2", "Judging", "https://huggingface.co/datasets/allenai/reward-bench-2", False),
}
LOWER_IS_BETTER = {"mae_expected_level"}
# Agent-safety sets (ATBench) plant credential-shaped strings on purpose. They are
# synthetic, but a public page must not carry anything a scanner reads as a key.
SECRET_SHAPES = re.compile(
    r"(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{8,}"      # Stripe
    r"|AKIA[0-9A-Z]{16}"                                 # AWS access key id
    r"|gh[pousr]_[A-Za-z0-9]{30,}"                       # GitHub tokens
    r"|xox[abprs]-[A-Za-z0-9-]{10,}"                     # Slack
    r"|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}"             # OpenAI, Anthropic
    r"|AIza[0-9A-Za-z_-]{35}"                            # Google API key
)


def clip(value, limit: int = TEXT_CLIP):
    """Shorten every string inside a state for display, keeping its shape,
    and redact credential-shaped strings."""
    if isinstance(value, str):
        value = SECRET_SHAPES.sub("[key-shaped string redacted]", value)
        return value if len(value) <= limit else value[:limit] + " …"
    if isinstance(value, dict):
        return {k: clip(v, limit) for k, v in value.items()}
    if isinstance(value, list):
        return [clip(v, limit) for v in value]
    return value


def latest_predictions(run_id: str) -> dict[str, dict]:
    path = C.RUNS / run_id / "predictions.jsonl"
    out: dict[str, dict] = {}
    if path.exists():
        for rec in C.read_jsonl(path):
            out[rec["case_id"]] = rec
    return out


def model_answer(rec: dict, case: dict) -> dict | None:
    """The part of a prediction the page shows for one example."""
    if not rec or rec.get("error") or rec.get("parse_error"):
        return {"failed": True}
    task = case["task_type"]
    if task == "rank":
        return {"scores": {k: round(v, 4) for k, v in rec["doc_scores"].items()}}
    if task == "noul":
        return {"p_true": round(rec["p_true"], 4), "correct": bool(case["gold"]) == (rec["p_true"] >= 0.5)}
    if task == "score":
        return {"expected": round(rec["expected_level"], 3), "pred": rec["pred"], "correct": rec["pred"] == case["gold"]}
    probs = rec.get("probabilities") or {}
    return {"pred": rec["pred"], "correct": str(rec["pred"]) == str(case["gold"]),
            "p_gold": round(probs.get(str(case["gold"]), 0.0), 4),
            "p_pred": round(probs.get(str(rec["pred"]), 0.0), 4)}


def example_view(case: dict, redistributable: bool) -> dict:
    question = case["question"] or next(iter(case["questions"].values()))
    instructions = question["instructions"].replace(C.UNTRUSTED_PREFIX, "").strip()
    view = {"case_id": case["case_id"], "task_type": case["task_type"], "gold": case["gold"],
            "question": instructions, "redistributable": redistributable}
    if case["task_type"] == "rank":
        state = case["state"]
        docs = state.get("documents") or {k: {"title": v.split(". ", 1)[0], "text": v.split(". ", 1)[-1]}
                                          for k, v in question["criteria"].items()}
        view["query"] = state["query"]
        view["documents"] = {k: {"title": d["title"][:200], "text": clip(d["text"], DOC_CLIP)} for k, d in docs.items()}
        view["protocol"] = case.get("rank_protocol")
        return view
    if redistributable:
        view["state"] = clip(case["state"])
        if question["type"] == "choice":
            view["options"] = {k: clip(str(v), 400) for k, v in question["criteria"].items()}
        elif question["type"] == "score":
            view["levels"] = question["criteria"]
    elif question["type"] == "choice":
        view["options"] = {k: k for k in question["criteria"]}
    if case.get("image_path"):
        src = C.DATA / case["image_path"] if not str(case["image_path"]).startswith("/") else None
        if src and src.exists():
            dest = SITE / "img" / str(case["image_path"]).replace("/", "_")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            view["image"] = f"img/{dest.name}"
    return view


def pick_examples(cases: list[dict]) -> list[dict]:
    base = [c for c in cases if c.get("perturbation", "none") == "none"]
    # A ranking example is only instructive if its shortlist holds a relevant document.
    if base and base[0]["task_type"] == "rank":
        base = [c for c in base if any(g > 0 for g in c["gold"].values())] or base
    elif base and base[0].get("rank_meta"):
        queries = {c["family_id"] for c in base if c["gold"] > 0}
        base = [c for c in base if c["family_id"] in queries] or base
    if len(base) <= EXAMPLES_PER_DATASET:
        return base
    step = len(base) / EXAMPLES_PER_DATASET
    return [base[int(i * step)] for i in range(EXAMPLES_PER_DATASET)]


def main() -> int:
    models = json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]
    sources = {s["key"]: s for s in C.load_manifest()["sources"]}
    keys = [k for k in C.available_case_keys() if k in DATASETS]

    results: dict[str, dict] = {}
    ranking: dict[str, dict] = {}
    shown_models = []
    raw: dict[str, dict] = {}
    for m in models:
        path = C.RUNS / m["run_id"] / "scores.json"
        extra = [C.RUNS / r / "scores.json" for r in m.get("also_read", [])]
        slices: dict = {}
        for p in [*extra, path]:
            if p.exists():
                slices.update(json.loads(p.read_text(encoding="utf-8"))["slices"])
        raw[m["name"]] = slices
        row = {}
        for key, s in slices.items():
            h = s.get("headline")
            if key not in DATASETS or not h:
                continue
            row[key] = {"value": round(h["value"], 4), "metric": h["metric"],
                        "ci": [round(x, 4) for x in h["ci95_bootstrap_by_family"]] if h.get("ci95_bootstrap_by_family") else None,
                        "coverage": round(s.get("coverage", 0), 4), "n": s.get("n_cases"),
                        "spearman": (s.get("metrics") or {}).get("spearman_expected_level")}
            if s.get("ranking"):
                ranking.setdefault(m["name"], {})[key] = {k: round(v, 4) for k, v in s["ranking"].items() if isinstance(v, float)}
        if row:
            results[m["name"]] = row
            shown_models.append({"name": m["name"], "hosting": m.get("hosting", "API"), "run_id": m["run_id"]})

    preds = {m["name"]: latest_predictions(m["run_id"]) for m in models if m["name"] in results}
    for m in models:
        for extra in m.get("also_read", []):
            if m["name"] in preds:
                preds[m["name"]].update(latest_predictions(extra))

    if (SITE / "img").exists():
        shutil.rmtree(SITE / "img")
    datasets, examples = [], {}
    for key in keys:
        name, group, url, adversarial = DATASETS[key]
        cases = C.read_cases(key)
        parent = sources.get(C.parent_key(key)) if not key.startswith(("mcp", "scifact", "nfcorpus", "helpsteer", "rewardbench")) else None
        redistributable = cases[0].get("redistributable", parent.get("redistributable", True) if parent else True)
        metric = next((results[mm][key]["metric"] for mm in results if key in results[mm]), None)
        cluster = next((c for c, ks in CLUSTERS.items() if key in ks), "Images" if group == "Images" else group)
        bm25 = next((r[key]["bm25_ndcg@10"] for r in ranking.values() if key in r and "bm25_ndcg@10" in r[key]), None)
        datasets.append({"key": key, "name": name, "group": group, "url": url, "adversarial": adversarial,
                         "cluster": cluster, "bm25": None if bm25 is None else round(100 * bm25, 1),
                         "task_type": cases[0]["task_type"], "cases": len(cases), "metric": metric,
                         "lower_is_better": metric in LOWER_IS_BETTER,
                         "license": cases[0].get("license") or (parent or {}).get("license"),
                         "redistributable": bool(redistributable)})
        rows = []
        for case in pick_examples(cases):
            view = example_view(case, bool(redistributable))
            view["answers"] = {mm: model_answer(preds[mm].get(case["case_id"]), case)
                               for mm in preds if preds[mm].get(case["case_id"])}
            rows.append(view)
        examples[key] = rows

    # The JevBench Index, computed exactly as readme_results.py does.
    info = slice_info(C.read_cases, {k for ks in CLUSTERS.values() for k in ks})
    index_rows = []
    for m in models:
        if m["name"] in MERGE.values() or not raw.get(m["name"]):
            continue
        slices = dict(raw[m["name"]])
        for k, v in raw.get(MERGE.get(m["name"], ""), {}).items():
            if not (slices.get(k) or {}).get("headline"):
                slices[k] = v
        unsupported = unsupported_keys(m, info)
        ix = index_for(slices, unsupported)
        per_dataset = {}
        for k in (k for ks in CLUSTERS.values() for k in ks):
            v = 0.0 if k in unsupported else to_100(k, slices.get(k))
            if v is not None:
                per_dataset[k] = round(v, 1)
        index_rows.append({"name": m["name"].replace(" (hosted)", ""), "hosting": m.get("hosting", "API"),
                           "index": None if ix["index"] is None else round(ix["index"], 1),
                           "clusters": {k: None if v is None else round(v, 1) for k, v in ix["clusters"].items()},
                           "zeroed": [DATASETS[k][0] for k in ix["zeroed"]], "missing": len(ix["missing"]),
                           "covered": ix["clusters_counted"], "complete": ix["complete"],
                           "scores": per_dataset, "unsupported": sorted(unsupported)})

    payload = {"generated": time.strftime("%Y-%m-%d"), "paper": PAPER, "citation": CITATION,
               "index": index_rows, "clusters": CLUSTERS,
               "models": shown_models, "datasets": datasets, "results": results,
               "ranking": ranking, "examples": examples}
    SITE.mkdir(exist_ok=True)
    out = SITE / "data.js"
    out.write_text("window.JEVBENCH = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    shutil.copyfile(C.ROOT.parent / "assets" / "jevbench-logo.svg", SITE / "logo.svg")
    shutil.copyfile(C.ROOT.parent / "assets" / "social-preview.png", SITE / "social-preview.png")
    print(f"wrote {out.relative_to(C.ROOT.parent)}: {len(shown_models)} models, {len(datasets)} datasets, "
          f"{sum(len(v) for v in examples.values())} examples, {out.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
