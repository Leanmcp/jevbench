"""Prove that djev actually consumes the state image, rather than just receiving it.

Sends each sampled case twice against the live endpoint: once with the image
attached, once with it stripped and nothing else changed. If the image were
ignored, input_tokens and the decision would be identical every time.

    uv run workspace/verify_images.py --slice vqa_rad --n 12

Writes data/runs/<run_id>/image_ablation.json. Costs 2 requests per case.
"""

from __future__ import annotations

import argparse
import json
import statistics

import common as C


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slice", default="vqa_rad")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--endpoint", default="djev")
    ap.add_argument("--run-id", default="djev-image-ablation")
    ap.add_argument("--timeout", type=float, default=300.0)
    args = ap.parse_args()

    endpoint = C.DJEV_URL if args.endpoint == "djev" else args.endpoint
    client = C.DecisionClient(endpoint=endpoint, model=None, require_key=False,
                             timeout=args.timeout, options={"seed": 0, "samples": 1})
    cases = C.read_cases(args.slice)[: args.n]
    print(f"{len(cases)} cases from {args.slice}, 2 requests each, endpoint {endpoint}\n")

    rows = []
    for case in cases:
        with_img = client.call(C.attach_images(case))
        without = client.call({k: v for k, v in case.items() if k != "image_path"})
        if not (with_img["ok"] and without["ok"]):
            print(f"  {case['case_id']}: request failed, skipped")
            continue
        a = C.parse_answer(with_img["response"], case["question_key"], case["task_type"])
        b = C.parse_answer(without["response"], case["question_key"], case["task_type"])
        ua = C.usage_of(with_img["response"])["input_tokens"]
        ub = C.usage_of(without["response"])["input_tokens"]
        rows.append({
            "case_id": case["case_id"],
            "gold": case["gold"],
            "tokens_with_image": ua,
            "tokens_without_image": ub,
            "token_delta": (ua - ub) if (ua and ub) else None,
            "pred_with_image": a.get("pred"),
            "pred_without_image": b.get("pred"),
            "decision_changed": a.get("pred") != b.get("pred"),
            "correct_with_image": a.get("pred") == case["gold"],
            "correct_without_image": b.get("pred") == case["gold"],
        })
        print(f"  {case['case_id']:28} tokens {ub:>5} -> {ua:>5} (+{ua-ub:>4})   "
              f"pred {str(b.get('pred')):>5} -> {str(a.get('pred')):>5}   gold {case['gold']}")

    if not rows:
        print("\nNo successful pairs. Is the endpoint up?")
        return 1

    deltas = [r["token_delta"] for r in rows if r["token_delta"] is not None]
    acc_with = statistics.fmean(1.0 if r["correct_with_image"] else 0.0 for r in rows)
    acc_without = statistics.fmean(1.0 if r["correct_without_image"] else 0.0 for r in rows)
    summary = {
        "slice": args.slice,
        "n_pairs": len(rows),
        "median_token_increase_from_image": statistics.median(deltas) if deltas else None,
        "min_token_increase": min(deltas) if deltas else None,
        "pairs_with_zero_token_increase": sum(1 for d in deltas if d == 0),
        "decisions_changed": sum(1 for r in rows if r["decision_changed"]),
        "accuracy_with_image": acc_with,
        "accuracy_without_image": acc_without,
        "interpretation": (
            "A token increase on every pair proves the image reaches the encoder. "
            "Accuracy higher with the image than without proves it is used, not just encoded."
        ),
    }
    out = C.RUNS / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "image_ablation.json").write_text(json.dumps({"summary": summary, "pairs": rows}, indent=2) + "\n", encoding="utf-8")

    print(f"\n{'-'*60}")
    print(f"pairs                        {summary['n_pairs']}")
    print(f"median token increase        +{summary['median_token_increase_from_image']}")
    print(f"pairs with zero increase     {summary['pairs_with_zero_token_increase']}  (any non-zero here would mean the image was dropped)")
    print(f"decisions changed by image   {summary['decisions_changed']}/{summary['n_pairs']}")
    print(f"accuracy WITH image          {acc_with*100:.1f}%")
    print(f"accuracy WITHOUT image       {acc_without*100:.1f}%")
    print(f"\nwrote {(out / 'image_ablation.json').relative_to(C.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
