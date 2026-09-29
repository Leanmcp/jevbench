"""Does CLM's accuracy collapse as the candidate set grows?

CLM answers a 2-option routing question at 0.996 and BANKING77's 77-option
version at 2.6%, which is twice chance. This sweeps the candidate count on the
same cases, always keeping the gold option in the set and filling the rest with
random distractors drawn from the real label set.

If accuracy falls off a cliff as k grows, the 77-option result is an artefact of
set size, not a measure of the model. If it is flat and low, the model genuinely
cannot do fine-grained intent classification.

    uv run workspace/probe_clm_options.py --n 150
    uv run workspace/probe_clm_options.py --n 150 --ks 2,5,10,20,40,77
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import random
import statistics

import common as C


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slice", default="banking77")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--ks", default="2,5,10,20,40,77")
    ap.add_argument("--endpoint", default="http://127.0.0.1:18700/v1/systemone")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    client = C.DecisionClient(endpoint=args.endpoint, model=None, require_key=False, timeout=300)
    cases = [c for c in C.read_cases(args.slice) if c["perturbation"] == "none"][: args.n]
    all_labels = sorted(C.read_cases(args.slice)[0]["question"]["criteria"].keys())
    print(f"{len(cases)} cases from {args.slice}, {len(all_labels)} labels available")
    print(f"endpoint {args.endpoint}\n")
    print(f"{'k':>4}  {'accuracy':>9}  {'chance':>7}  {'ratio':>6}  n")

    ks = [int(x) for x in args.ks.split(",")]
    for k in ks:
        k = min(k, len(all_labels))

        def one(case, k=k):
            rng = random.Random(args.seed + case["row_index"])
            gold = str(case["gold"])
            others = [l for l in all_labels if l != gold]
            chosen = rng.sample(others, min(k - 1, len(others)))
            options = chosen + [gold]
            rng.shuffle(options)
            q = {
                "type": "choice",
                "instructions": case["question"]["instructions"],
                "criteria": {o: o.replace("_", " ") for o in options},
            }
            r = client.call(dict(case, question=q))
            if not r["ok"]:
                return None
            parsed = C.parse_answer(r["response"], case["question_key"], "choice")
            if parsed.get("pred") is None:
                return None
            return 1.0 if str(parsed["pred"]) == gold else 0.0

        with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            got = [v for v in pool.map(one, cases) if v is not None]
        acc = statistics.fmean(got) if got else 0.0
        chance = 1.0 / k
        print(f"{k:>4}  {acc*100:>8.1f}%  {chance*100:>6.1f}%  {acc/chance:>5.1f}x  {len(got)}")

    print("\nA ratio near 1.0x means no signal at that set size.")
    print("A high ratio at small k that collapses toward 1.0x as k grows means the")
    print("77-option result measures set size, not the model.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
