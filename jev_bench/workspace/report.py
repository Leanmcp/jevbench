"""Step 3e: print the final results and write them as markdown.

    uv run workspace/report.py --latest
    uv run workspace/report.py --run-id jev-1.13.0-20260926T141500
    uv run workspace/report.py --latest --compare djev-0.1-20260927T090000

Reads data/runs/<run_id>/scores.json, prints the tables, and writes
reports/RESULTS_<run_id>.md. Caveats are generated from what the run actually
contains, so a truncated slice or a polarity warning cannot quietly drop out of
the write-up.
"""

from __future__ import annotations

import argparse
import json

import common as C


def fmt(value, digits: int = 4, pct: bool = False) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%" if pct else f"{value:.{digits}f}"
    return str(value)


def load_scores(run_id: str | None, latest: bool) -> dict:
    if latest or not run_id:
        runs = sorted((p for p in C.RUNS.glob("*") if (p / "scores.json").exists()), key=lambda p: p.stat().st_mtime)
        if not runs:
            raise SystemExit("No scored runs found. Run workspace/score_runs.py first.")
        path = runs[-1] / "scores.json"
    else:
        path = C.RUNS / run_id / "scores.json"
        if not path.exists():
            raise SystemExit(f"{path} does not exist. Run score_runs.py --run-id {run_id} first.")
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(rows: list[list[str]], headers: list[str]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


def build(scores: dict, compare: dict | None) -> str:
    meta = scores.get("meta", {})
    slices = scores["slices"]
    lines: list[str] = []
    add = lines.append

    add(f"# jev-bench results: {scores['run_id']}")
    add("")
    add(f"Scored {scores['scored_at']}. Model requested `{meta.get('model_requested', 'unknown')}`, endpoint `{meta.get('endpoint', 'unknown')}`, "
        f"manifest pinned {meta.get('manifest_pinned_on', 'unknown')}. One typed question per request.")
    add("")

    # headline
    rows = []
    for key in sorted(slices):
        s = slices[key]
        h = s.get("headline")
        if not h:
            rows.append([key, s["task_type"], s["n_cases"], fmt(s["coverage"], pct=True), "no usable records", "n/a", "n/a"])
            continue
        ci = h["ci95_bootstrap_by_family"]
        rows.append([
            key, s["task_type"], s["n_cases"], fmt(s["coverage"], pct=True),
            f"**{fmt(h['value'])}**", f"[{fmt(ci[0], 3)}, {fmt(ci[1], 3)}]" if ci else "n/a", h["metric"],
        ])
    add("## Headline")
    add("")
    add(md_table(rows, ["slice", "type", "cases", "coverage", "value", "95% CI", "metric"]))
    add("")
    add("Confidence intervals are percentile bootstrap over "
        f"{scores['conventions']['bootstrap_resamples']} resamples grouped by `family_id`, so a case and its reordered twin move together. "
        "Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.")
    add("")

    # choice detail
    choice_rows = []
    for key in sorted(slices):
        s = slices[key]
        if s["task_type"] != "choice" or "metrics" not in s:
            continue
        m = s["metrics"]
        choice_rows.append([
            key, m["n_scored"], m["n_classes_in_gold"], fmt(m["accuracy"], pct=True), fmt(m["macro_f1"]),
            fmt(m["brier_sum_convention"]), fmt(m["nll_excluding_zero_gold"]), m["n_zero_probability_on_gold"],
            fmt(m["ece_10_bins"]), m["n_with_probabilities"],
        ])
    if choice_rows:
        add("## Choice slices")
        add("")
        add(md_table(choice_rows, ["slice", "n", "gold classes", "accuracy", "macro-F1", "Brier", "NLL", "zero-prob on gold", "ECE (10 bins)", "n with probs"]))
        add("")
        add("Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; "
            "that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.")
        add("")

    # noul detail
    noul_rows = []
    for key in sorted(slices):
        s = slices[key]
        if s["task_type"] != "noul" or "metrics" not in s:
            continue
        m = s["metrics"]
        noul_rows.append([
            key, m["n_scored"], fmt(m["accuracy_at_0.5"], pct=True), fmt(m["accuracy_if_polarity_flipped"], pct=True),
            fmt(m["positive_class_recall"], pct=True), fmt(m["false_positive_rate"], pct=True), fmt(m["auroc"]),
            fmt(m["brier"]), fmt(m["ece_10_bins"]), fmt(m["base_rate_positive"], pct=True),
        ])
    if noul_rows:
        add("## Binary slices")
        add("")
        add(md_table(noul_rows, ["slice", "n", "acc @0.5", "acc if flipped", "positive recall", "FPR", "AUROC", "Brier", "ECE", "base rate"]))
        add("")
        add("`acc if flipped` exists because two upstream cards never state which integer means unsafe. If that column is the higher one, "
            "the mapping in `common.POLARITY_ASSUMPTIONS` is wrong and neither number should be quoted until it is fixed. "
            "AUROC is threshold-free, so it is the fairer comparison between models with differently placed probabilities.")
        add("")

    # ordinal detail
    ord_rows = []
    for key in sorted(slices):
        s = slices[key]
        if s["task_type"] != "score" or "metrics" not in s:
            continue
        m = s["metrics"]
        ord_rows.append([key, m["n_scored"], m["n_levels_observed"], fmt(m["exact_accuracy_rounded"], pct=True),
                         fmt(m["within_one_level"], pct=True), fmt(m["mae_expected_level"], 3), fmt(m["ranked_probability_score"])])
    if ord_rows:
        add("## Ordinal slices")
        add("")
        add(md_table(ord_rows, ["slice", "n", "levels", "exact (rounded)", "within 1 level", "MAE (expected level)", "RPS"]))
        add("")
        add("The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. "
            "Levels are treated as equally spaced, which SST-5 does not actually guarantee.")
        add("")

    # position bias
    pb_rows = []
    for key in sorted(slices):
        pb = slices[key].get("position_bias")
        if not pb or not pb.get("n_families_with_both"):
            continue
        by = pb["accuracy_by_perturbation"]
        pb_rows.append([key, pb["n_families_with_both"], fmt(by.get("none"), pct=True), fmt(by.get("permuted"), pct=True),
                        fmt(pb.get("both_variants_correct"), pct=True), fmt(pb.get("flipped_by_reordering"), pct=True)])
    if pb_rows:
        add("## Option-order sensitivity")
        add("")
        add(md_table(pb_rows, ["slice", "families with both", "original order", "permuted order", "both correct", "flipped by reordering"]))
        add("")
        add("`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. "
            "Reordering does not change the question, so anything materially above zero is position bias, not difficulty.")
        add("")

    # runtime
    rt_rows = []
    for key in sorted(slices):
        rt = slices[key].get("runtime")
        if not rt:
            continue
        rt_rows.append([key, fmt(rt["latency_ms_p50"], 0), fmt(rt["latency_ms_p95"], 0), fmt(rt["latency_ms_p99"], 0),
                        fmt(rt["input_tokens_mean"], 0), f"{rt['input_tokens_total']:,}" if rt["input_tokens_total"] else "n/a", rt["retries"]])
    if rt_rows:
        add("## Runtime")
        add("")
        add(md_table(rt_rows, ["slice", "p50 ms", "p95 ms", "p99 ms", "mean input tokens", "total input tokens", "retries"]))
        add("")
        add(f"Measured end to end from this client at concurrency {meta.get('concurrency', 'unknown')}, which is a property of this machine and network "
            "as much as of the model. Token counts are the API's own `usage`, not an estimate.")
        add("")

    if compare:
        add("## Comparison")
        add("")
        c_rows = []
        for key in sorted(set(slices) & set(compare["slices"])):
            a, b = slices[key].get("headline"), compare["slices"][key].get("headline")
            if not a or not b or a["metric"] != b["metric"]:
                continue
            delta = a["value"] - b["value"]
            c_rows.append([key, a["metric"], fmt(a["value"]), fmt(b["value"]), f"{delta:+.4f}"])
        add(md_table(c_rows, ["slice", "metric", scores["run_id"], compare["run_id"], "delta"]))
        add("")
        add("These are unpaired point differences. A paired bootstrap on shared case ids is the right test before claiming one model beats the other.")
        add("")

    # caveats, generated from the run
    add("## What these numbers do not establish")
    add("")
    truncated = {k: v["n_truncated_states"] for k, v in slices.items() if v.get("n_truncated_states")}
    if truncated:
        add(f"- **Truncated states.** {', '.join(f'{k}: {n}' for k, n in truncated.items())}. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.")
    exposed = []
    for key in sorted(slices):
        try:
            src = C.source_by_key(C.parent_key(key))
        except KeyError:
            continue
        if src["exposure"] in {"reported", "likely"}:
            exposed.append(f"{key} ({src['exposure']})")
    if exposed:
        add(f"- **Training exposure.** {', '.join(exposed)}. Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.")
    errored = {k: v["n_errors"] for k, v in slices.items() if v.get("n_errors")}
    if errored:
        add(f"- **Failed requests.** {', '.join(f'{k}: {n}' for k, n in errored.items())}. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.")
    add("- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.")
    add("- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.")
    add("- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.")
    add("- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.")
    add("")
    add(f"Artifacts: `data/runs/{scores['run_id']}/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.")
    add("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--compare", default=None, metavar="RUN_ID")
    args = ap.parse_args()

    scores = load_scores(args.run_id, args.latest)
    compare = load_scores(args.compare, False) if args.compare else None
    text = build(scores, compare)

    C.REPORTS.mkdir(parents=True, exist_ok=True)
    out = C.REPORTS / f"RESULTS_{scores['run_id']}.md"
    out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nwrote {out.relative_to(C.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
