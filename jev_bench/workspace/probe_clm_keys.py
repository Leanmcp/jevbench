"""Does CLM key its choice on the criterion NAME or the DESCRIPTION?

Our MCQ adapter puts the answer text in the description and uses bare letters as
criterion names, which suits a model that reads descriptions. CLM is a dual
encoder that matches a state embedding against action embeddings, so if the
action text is the criterion NAME, a letter carries no signal and accuracy
collapses to chance or below.

Three variants of the same cases, same model, same endpoint:
  A  letters as names, answer text as description   (what the harness sends now)
  B  answer text as name, no description
  C  answer text as name, answer text as description

    uv run workspace/probe_clm_keys.py --slice medmcqa --n 200
"""
from __future__ import annotations

import argparse
import statistics

import common as C

LIMIT_NAME = 500  # djev and CLM both cap a criterion name at 500 characters


def variant(case: dict, mode: str) -> tuple[dict, str]:
    """Return (question, gold) rebuilt under one naming convention."""
    q = case["question"]
    criteria = q["criteria"]
    gold_letter = str(case["gold"])
    if mode == "A":
        return q, gold_letter
    texts = {k: str(v)[:LIMIT_NAME] for k, v in criteria.items()}
    # Names must stay unique; if two options share text, this case is unusable.
    if len(set(texts.values())) != len(texts):
        return None, None
    gold_text = texts[gold_letter]
    if mode == "B":
        new = {t: None for t in texts.values()}
    else:
        new = {t: t for t in texts.values()}
    return {"type": "choice", "instructions": q["instructions"], "criteria": new}, gold_text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slice", default="medmcqa")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--endpoint", default="http://127.0.0.1:18700/v1/systemone")
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()

    import concurrent.futures as cf

    client = C.DecisionClient(endpoint=args.endpoint, model=None, require_key=False, timeout=300)
    cases = C.read_cases(args.slice)[: args.n]
    print(f"{len(cases)} cases from {args.slice}, three naming conventions, endpoint {args.endpoint}\n")

    results: dict[str, list[float]] = {}
    for mode in ("A", "B", "C"):
        def one(case, mode=mode):
            q, gold = variant(case, mode)
            if q is None:
                return None
            probe = dict(case, question=q, gold=gold)
            r = client.call(probe)
            if not r["ok"]:
                return None
            parsed = C.parse_answer(r["response"], case["question_key"], "choice")
            if parsed.get("pred") is None:
                return None
            return 1.0 if str(parsed["pred"]) == str(gold) else 0.0

        with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            got = [v for v in pool.map(one, cases) if v is not None]
        results[mode] = got
        acc = statistics.fmean(got) if got else 0.0
        label = {"A": "letters as names, text in description (current harness)",
                 "B": "answer text as name, no description",
                 "C": "answer text as name and description"}[mode]
        print(f"  {mode}  {acc*100:5.1f}%  ({len(got)} scored)   {label}")

    best = max(results, key=lambda m: statistics.fmean(results[m]) if results[m] else 0)
    print(f"\nchance for 4 options is 25.0%")
    print(f"best convention: {best}")
    if best != "A":
        a = statistics.fmean(results["A"]) * 100
        b = statistics.fmean(results[best]) * 100
        print(f"CLM keys on the criterion NAME: {a:.1f}% -> {b:.1f}% ({b-a:+.1f} points) by moving the text into the name.")
        print("The harness needs a per-model naming convention, and that is a finding, not a bug fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
