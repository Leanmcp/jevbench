"""The JevBench Index: one 0-100 number per model.

1. Every dataset on 0-100: accuracy as is, nDCG@10 and Spearman x 100,
   SST-5 as 100 x (1 - MAE / 4), since 4 is the largest possible error.
2. Six clusters, each the plain average of its datasets.
3. Index = the plain average of the six clusters, so no cluster outweighs
   another however many datasets it holds.

Datasets a model has not run yet are left out: each cluster averages the
datasets it has, and the index averages the clusters it has, reported with how
many of the six it covers, e.g. 73.0 (4/6). A dataset the model's API
rejects outright (option limits, question types) counts as 0, since the model
cannot do it. Ranking uses the per-document protocol only, so each ranking dataset
counts once. Image slices are left out: only one model
takes images.
"""

from __future__ import annotations

CLUSTERS = {
    "Science": ["medmcqa", "medqa_usmle", "pubmedqa", "mmlu_pro", "scienceqa_text"],
    "Tool calling": ["mcpbench_server_routing", "mcpbench_tool_selection", "mcpmark_server_routing", "mcpmark_tool_selection"],
    "Business": ["banking77", "sst5"],
    "Selection": ["aegis2", "aegis2_response", "atbench500", "jailbreak_classification", "prompt_injections"],
    "Ranking": ["scifact_rank_noul", "nfcorpus_rank_noul"],
    "Judging": ["helpsteer2_helpfulness", "rewardbench2"],
}


# The same hosted D1 service reached two ways; OpenRouter fills what the free
# tier was too slow for, so the two count as one model.
MERGE = {"Liquid D1 (hosted)": "Liquid D1 via OpenRouter"}


def slice_info(read_cases, keys) -> dict[str, dict]:
    """Largest option count and question type per slice, for unsupported_keys."""
    out = {}
    for k in keys:
        cases = read_cases(k)
        out[k] = {"max_options": max(c.get("n_options") or 0 for c in cases), "task_type": cases[0]["task_type"]}
    return out


def to_100(key: str, entry: dict | None) -> float | None:
    """One dataset's headline on a 0-100, higher-is-better scale."""
    if not entry or not entry.get("headline"):
        return None
    if key == "helpsteer2_helpfulness":
        sp = (entry.get("metrics") or {}).get("spearman_expected_level")
        return None if sp is None else 100 * sp
    h = entry["headline"]
    if h["metric"] == "mae_expected_level":
        return 100 * (1 - h["value"] / 4)
    return 100 * h["value"]


def unsupported_keys(model: dict, slice_info: dict[str, dict]) -> set[str]:
    """Datasets the model's API rejects outright: too many options, or a question type it does not take."""
    out = set()
    for key, info in slice_info.items():
        if model.get("max_options") and info["max_options"] > model["max_options"]:
            out.add(key)
        if model.get("task_types") and info["task_type"] not in model["task_types"]:
            out.add(key)
    return out


def index_for(slices: dict, unsupported: set[str] = frozenset()) -> dict:
    """{'clusters': {name: score or None}, 'index': score or None, 'missing': [keys],
    'zeroed': [keys]}. A dataset the API rejects counts as 0: the model cannot do it."""
    clusters, missing = {}, []
    zeroed = sorted(k for keys in CLUSTERS.values() for k in keys if k in unsupported)
    for name, keys in CLUSTERS.items():
        vals = [0.0 if k in unsupported else to_100(k, slices.get(k)) for k in keys]
        missing += [k for k, v in zip(keys, vals) if v is None]
        have = [v for v in vals if v is not None]
        clusters[name] = sum(have) / len(have) if have else None
    counted = [v for v in clusters.values() if v is not None]
    return {"clusters": clusters, "index": sum(counted) / len(counted) if counted else None,
            "clusters_counted": len(counted), "complete": not missing,
            "missing": missing, "zeroed": zeroed}
