"""Step 3d: score a run.

    uv run workspace/score_runs.py --run-id jev-1.13.0-20260926T141500
    uv run workspace/score_runs.py --latest

Writes data/runs/<run_id>/scores.json and prints a compact summary. report.py
turns that JSON into the final markdown tables.

Metric choices, stated rather than implied:

- Brier for a K-class decision is mean_i sum_k (p_ik - y_ik)^2, the sum
  convention, not averaged over classes.
- NLL is -log p(gold). Cases where p(gold) is exactly zero are counted and
  reported separately instead of being hidden by clipping; a clipped value at
  1e-12 is also given, labelled as clipped.
- ECE uses 10 equal-width bins on the top predicted probability. Binning changes
  the number, so the bin count travels with it.
- Ordinal slices get MAE on the expected level and the ranked probability score.
- Confidence intervals are percentile bootstrap over 2000 resamples grouped by
  family_id, so a case and its permuted twin move together.
- For a noul slice whose upstream card never states label polarity, accuracy is
  reported both ways. If the flipped number is the high one, the mapping in
  common.POLARITY_ASSUMPTIONS is wrong.
- best_threshold_accuracy is chosen on the very data it scores, so it is an
  optimistic diagnostic and is labelled that way, not an operating point.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import random
import statistics

import common as C

BOOTSTRAP_N = 2000
ECE_BINS = 10
CLIP = 1e-12


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    return s[min(len(s) - 1, int(len(s) * p))]


def macro_f1(pairs: list[tuple[str, str]]) -> tuple[float, dict]:
    labels = sorted({g for g, _ in pairs} | {p for _, p in pairs})
    per: dict[str, dict] = {}
    f1s = []
    for label in labels:
        tp = sum(1 for g, p in pairs if g == label and p == label)
        fp = sum(1 for g, p in pairs if g != label and p == label)
        fn = sum(1 for g, p in pairs if g == label and p != label)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        support = tp + fn
        if support:
            f1s.append(f1)
        per[label] = {"precision": prec, "recall": rec, "f1": f1, "support": support}
    return (statistics.fmean(f1s) if f1s else 0.0), per


def ece(confidences: list[float], correct: list[bool], bins: int = ECE_BINS) -> float | None:
    if not confidences:
        return None
    total = len(confidences)
    out = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, c in enumerate(confidences) if (c > lo or (b == 0 and c >= lo)) and c <= hi]
        if not idx:
            continue
        acc = sum(correct[i] for i in idx) / len(idx)
        conf = statistics.fmean(confidences[i] for i in idx)
        out += len(idx) / total * abs(acc - conf)
    return out


def auroc(scores: list[float], labels: list[bool]) -> float | None:
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    ranked = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores)
    i = 0
    while i < len(ranked):
        j = i
        while j + 1 < len(ranked) and scores[ranked[j + 1]] == scores[ranked[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[ranked[k]] = avg
        i = j + 1
    rank_sum = sum(ranks[i] for i, y in enumerate(labels) if y)
    n_pos, n_neg = len(pos), len(neg)
    return (rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def bootstrap_ci(units: list[list[float]], seed: int = 7) -> tuple[float, float] | None:
    """Percentile CI for a mean, resampling whole families."""
    if len(units) < 5:
        return None
    rng = random.Random(seed)
    means = []
    for _ in range(BOOTSTRAP_N):
        pick = [units[rng.randrange(len(units))] for _ in range(len(units))]
        flat = [v for group in pick for v in group]
        if flat:
            means.append(statistics.fmean(flat))
    means.sort()
    return means[int(0.025 * len(means))], means[int(0.975 * len(means))]


def score_choice(recs: list[dict]) -> dict:
    pairs = [(str(r["gold"]), str(r["pred"])) for r in recs]
    correct = [g == p for g, p in pairs]
    acc = statistics.fmean(1.0 if c else 0.0 for c in correct)
    mf1, per_class = macro_f1(pairs)

    briers: list[float] = []
    nlls: list[float] = []
    nlls_clipped: list[float] = []
    confs: list[float] = []
    correct_with_probs: list[bool] = []
    zero_gold = 0
    for r in recs:
        probs = r.get("probabilities")
        if not probs:
            continue
        total = sum(probs.values()) or 1.0
        norm = {k: v / total for k, v in probs.items()}
        gold = str(r["gold"])
        p_gold = norm.get(gold, 0.0)
        briers.append(sum((p - (1.0 if k == gold else 0.0)) ** 2 for k, p in norm.items()))
        if p_gold <= 0:
            zero_gold += 1
        else:
            nlls.append(-math.log(p_gold))
        nlls_clipped.append(-math.log(max(CLIP, p_gold)))
        confs.append(max(norm.values()))
        correct_with_probs.append(gold == str(r["pred"]))

    out = {
        "n_scored": len(recs),
        "accuracy": acc,
        "macro_f1": mf1,
        "n_classes_in_gold": len({g for g, _ in pairs}),
        "per_class": per_class if len(per_class) <= 12 else {"note": f"{len(per_class)} classes, see scores.json consumers", "worst_5": dict(sorted(per_class.items(), key=lambda kv: kv[1]["f1"])[:5])},
        "brier_sum_convention": statistics.fmean(briers) if briers else None,
        "nll_excluding_zero_gold": statistics.fmean(nlls) if nlls else None,
        "n_zero_probability_on_gold": zero_gold,
        "nll_clipped_1e-12": statistics.fmean(nlls_clipped) if nlls_clipped else None,
        "ece_10_bins": ece(confs, correct_with_probs) if confs else None,
        "n_with_probabilities": len(briers),
    }
    return out


def score_noul(recs: list[dict], slice_key: str) -> dict:
    golds = [bool(r["gold"]) for r in recs]
    ps = [float(r["p_true"]) for r in recs]
    preds = [p >= 0.5 for p in ps]
    acc = statistics.fmean(1.0 if g == p else 0.0 for g, p in zip(golds, preds))

    tp = sum(1 for g, p in zip(golds, preds) if g and p)
    fp = sum(1 for g, p in zip(golds, preds) if not g and p)
    fn = sum(1 for g, p in zip(golds, preds) if g and not p)
    tn = sum(1 for g, p in zip(golds, preds) if not g and not p)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0

    thresholds = sorted({round(p, 3) for p in ps} | {0.5})
    best = max(thresholds, key=lambda t: statistics.fmean(1.0 if g == (p >= t) else 0.0 for g, p in zip(golds, ps)))
    best_acc = statistics.fmean(1.0 if g == (p >= best) else 0.0 for g, p in zip(golds, ps))

    out = {
        "n_scored": len(recs),
        "accuracy_at_0.5": acc,
        "accuracy_if_polarity_flipped": statistics.fmean(1.0 if g != p else 0.0 for g, p in zip(golds, preds)),
        "positive_class_precision": prec,
        "positive_class_recall": rec,
        "positive_class_f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "brier": statistics.fmean((p - (1.0 if g else 0.0)) ** 2 for p, g in zip(ps, golds)),
        "nll_excluding_zeros": (lambda vals: statistics.fmean(vals) if vals else None)(
            [-math.log(p if g else 1 - p) for p, g in zip(ps, golds) if (p if g else 1 - p) > 0]
        ),
        "n_zero_probability_on_gold": sum(1 for p, g in zip(ps, golds) if (p if g else 1 - p) <= 0),
        "ece_10_bins": ece([max(p, 1 - p) for p in ps], [g == pr for g, pr in zip(golds, preds)]),
        "auroc": auroc(ps, golds),
        "best_threshold_optimistic": best,
        "best_threshold_accuracy_optimistic": best_acc,
        "mean_p_true": statistics.fmean(ps),
        "base_rate_positive": statistics.fmean(1.0 if g else 0.0 for g in golds),
    }
    if slice_key in C.POLARITY_ASSUMPTIONS:
        out["polarity_assumption"] = C.POLARITY_ASSUMPTIONS[slice_key]
    return out


def score_ordinal(recs: list[dict]) -> dict:
    golds = [int(r["gold"]) for r in recs]
    exps = [float(r["expected_level"]) for r in recs]
    preds = [int(round(e)) for e in exps]
    k = max(max(golds), max(preds)) + 1

    rps = []
    for r in recs:
        probs = r.get("probabilities")
        if not probs:
            continue
        levels = sorted(probs, key=lambda key: (len(key), key))
        vals = [probs[key] for key in levels]
        total = sum(vals) or 1.0
        vals = [v / total for v in vals]
        gold = int(r["gold"])
        cum_p = cum_y = 0.0
        acc = 0.0
        for i, v in enumerate(vals):
            cum_p += v
            cum_y += 1.0 if i == gold else 0.0
            acc += (cum_p - cum_y) ** 2
        rps.append(acc / max(1, len(vals) - 1))

    return {
        "n_scored": len(recs),
        "exact_accuracy_rounded": statistics.fmean(1.0 if g == p else 0.0 for g, p in zip(golds, preds)),
        "within_one_level": statistics.fmean(1.0 if abs(g - p) <= 1 else 0.0 for g, p in zip(golds, preds)),
        "mae_expected_level": statistics.fmean(abs(g - e) for g, e in zip(golds, exps)),
        "mae_rounded": statistics.fmean(abs(g - p) for g, p in zip(golds, preds)),
        "ranked_probability_score": statistics.fmean(rps) if rps else None,
        "n_levels_observed": k,
        "note": "Levels are treated as equally spaced, which SST-5 does not guarantee.",
    }


def headline_units(recs: list[dict], task_type: str) -> tuple[str, list[list[float]]]:
    groups: dict[str, list[float]] = collections.defaultdict(list)
    for r in recs:
        if task_type == "score":
            groups[r["family_id"]].append(abs(int(r["gold"]) - float(r["expected_level"])))
        elif task_type == "noul":
            groups[r["family_id"]].append(1.0 if bool(r["gold"]) == (float(r["p_true"]) >= 0.5) else 0.0)
        else:
            groups[r["family_id"]].append(1.0 if str(r["gold"]) == str(r["pred"]) else 0.0)
    name = "mae_expected_level" if task_type == "score" else "accuracy"
    return name, list(groups.values())


def is_correct(rec: dict, task_type: str) -> bool:
    if task_type == "choice":
        return str(rec["gold"]) == str(rec.get("pred"))
    if task_type == "noul":
        return bool(rec["gold"]) == (float(rec["p_true"]) >= 0.5)
    return int(rec["gold"]) == int(round(float(rec["expected_level"])))


def position_bias(recs: list[dict], task_type: str) -> dict | None:
    by_pert: dict[str, list[float]] = collections.defaultdict(list)
    families: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    for r in recs:
        ok = is_correct(r, task_type)
        by_pert[r["perturbation"]].append(1.0 if ok else 0.0)
        families[r["family_id"]][r["perturbation"]] = ok
    if len(by_pert) < 2:
        return None
    both = [f for f in families.values() if len(f) >= 2]
    return {
        "accuracy_by_perturbation": {k: statistics.fmean(v) for k, v in sorted(by_pert.items())},
        "n_families_with_both": len(both),
        "both_variants_correct": statistics.fmean(1.0 if all(f.values()) else 0.0 for f in both) if both else None,
        "flipped_by_reordering": statistics.fmean(1.0 if len(set(f.values())) > 1 else 0.0 for f in both) if both else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--latest", action="store_true")
    args = ap.parse_args()

    if args.latest or not args.run_id:
        runs = sorted((p for p in C.RUNS.glob("*") if (p / "predictions.jsonl").exists()), key=lambda p: p.stat().st_mtime)
        if not runs:
            print("No runs found under data/runs/. Run workspace/run_eval.py first.")
            return 2
        run_dir = runs[-1]
    else:
        run_dir = C.RUNS / args.run_id
    run_id = run_dir.name
    preds = C.read_jsonl(run_dir / "predictions.jsonl")
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8")) if (run_dir / "meta.json").exists() else {}
    print(f"run {run_id}: {len(preds):,} prediction records")

    # last record wins, so a resumed run does not double count
    latest: dict[str, dict] = {}
    for rec in preds:
        latest[rec["case_id"]] = rec
    records = list(latest.values())

    by_slice: dict[str, list[dict]] = collections.defaultdict(list)
    for rec in records:
        by_slice[rec["slice"]].append(rec)

    scores: dict[str, dict] = {}
    table_rows = []
    for slice_key in sorted(by_slice):
        recs = by_slice[slice_key]
        task_type = recs[0]["task_type"]
        errors = [r for r in recs if r.get("error")]
        parse_errors = [r for r in recs if not r.get("error") and r.get("parse_error")]
        usable = [r for r in recs if not r.get("error") and not r.get("parse_error") and r.get("pred") is not None]

        entry: dict = {
            "slice": slice_key,
            "task_type": task_type,
            "n_cases": len(recs),
            "n_errors": len(errors),
            "n_parse_errors": len(parse_errors),
            "coverage": len(usable) / len(recs) if recs else 0.0,
            "n_truncated_states": sum(1 for r in recs if r.get("truncated_state")),
            "error_examples": sorted({str(r.get("error"))[:120] for r in errors})[:3],
        }
        if usable:
            if task_type == "choice":
                entry["metrics"] = score_choice(usable)
            elif task_type == "noul":
                entry["metrics"] = score_noul(usable, slice_key)
            else:
                entry["metrics"] = score_ordinal(usable)

            name, units = headline_units(usable, task_type)
            ci = bootstrap_ci(units)
            entry["headline"] = {
                "metric": name,
                "value": statistics.fmean(v for group in units for v in group),
                "ci95_bootstrap_by_family": list(ci) if ci else None,
                "n_families": len(units),
            }
            entry["position_bias"] = position_bias(usable, task_type)

            lat = [r["latency_ms"] for r in usable if r.get("latency_ms")]
            toks = [r["input_tokens"] for r in usable if r.get("input_tokens")]
            entry["runtime"] = {
                "latency_ms_p50": percentile(lat, 0.5),
                "latency_ms_p95": percentile(lat, 0.95),
                "latency_ms_p99": percentile(lat, 0.99),
                "input_tokens_mean": statistics.fmean(toks) if toks else None,
                "input_tokens_total": sum(toks) if toks else None,
                "retries": sum((r.get("attempts") or 1) - 1 for r in usable),
            }
            h = entry["headline"]
            table_rows.append([
                slice_key, task_type, len(recs), f"{entry['coverage']*100:.0f}%",
                f"{h['value']:.4f}", f"[{h['ci95_bootstrap_by_family'][0]:.3f}, {h['ci95_bootstrap_by_family'][1]:.3f}]" if h["ci95_bootstrap_by_family"] else "n/a",
                h["metric"], f"{entry['runtime']['latency_ms_p50']:.0f}" if entry["runtime"]["latency_ms_p50"] else "n/a",
            ])
        else:
            table_rows.append([slice_key, task_type, len(recs), "0%", "n/a", "n/a", "no usable records", "n/a"])
        scores[slice_key] = entry

    payload = {
        "run_id": run_id,
        "meta": meta,
        "scored_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "conventions": {
            "brier": "mean_i sum_k (p_ik - y_ik)^2",
            "ece_bins": ECE_BINS,
            "bootstrap_resamples": BOOTSTRAP_N,
            "bootstrap_unit": "family_id",
            "nll": "-log p(gold), zeros counted separately, clipped variant labelled",
            "one_question_per_request": True,
        },
        "slices": scores,
    }
    out = run_dir / "scores.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")

    print()
    print(C.table(table_rows, ["slice", "type", "cases", "coverage", "headline", "95% CI", "metric", "p50 ms"]))
    print(f"\nwrote {out.relative_to(C.ROOT)}")

    flips = [k for k, v in scores.items() if v.get("metrics", {}).get("accuracy_if_polarity_flipped", 0) > v.get("metrics", {}).get("accuracy_at_0.5", 1)]
    if flips:
        print("\nPOLARITY WARNING: flipped accuracy is higher for " + ", ".join(flips))
        print("Fix the mapping in common.POLARITY_ASSUMPTIONS and rescore. Do not report either number until it is settled.")
    print(f"\nNext: uv run workspace/report.py --run-id {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
