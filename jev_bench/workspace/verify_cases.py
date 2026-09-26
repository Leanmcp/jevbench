"""Step 3b: verify the built cases before spending a single API call.

Six checks, all offline:

1. case ids are unique
2. gold is reachable: a choice gold is one of the presented option keys, a noul
   gold is a boolean, a score gold is a valid level index
3. no hidden field leaks into the state, checked against the original rows
4. request limits: options per question, instruction length, score levels,
   state size
5. context budget triage: how many cases exceed 512 / 1024 / 4096 estimated tokens
6. one rendered request per slice is written to data/cases/previews/ for eyeball
   review, as a file rather than on stdout, because several slices contain
   adversarial text

    uv run workspace/verify_cases.py
    uv run workspace/verify_cases.py --only atbench500

Exit code is non-zero if any hard check fails. Hard failures are duplicate ids,
unreachable gold, leaked hidden fields and exceeded hard limits.
"""

from __future__ import annotations

import argparse
import json

import build_cases as B
import common as C

# djev's documented limits. Laya's HTTP guard is stricter on options (100) and
# the Jev API's own limits are not published, so these are the binding numbers
# we can actually cite, and the Laya figure is reported as a warning.
LIMIT_OPTIONS_DJEV = 255
LIMIT_OPTIONS_LAYA = 100
LIMIT_SCORE_LEVELS = (2, 10)
LIMIT_INSTRUCTIONS = 2000
LIMIT_STATE_CHARS = 20_000
LIMIT_CRITERION_NAME = 500

# Fields that are gold rationales or gold-adjacent annotations. Leaking any of
# these is a silent benchmark failure, so they are checked at a lower threshold.
RATIONALE_FIELDS = {"exp", "cot_content", "long_answer", "solution", "lecture", "metamap_phrases"}
MIN_LEAK_LEN = 24
MIN_RATIONALE_LEN = 12


def check_slice(slice_key: str, verbose: bool) -> tuple[list[str], list[str], dict]:
    hard: list[str] = []
    soft: list[str] = []
    cases = C.read_cases(slice_key)
    src = C.source_by_key(C.parent_key(slice_key))
    rows, _, _ = B.rows_for_slice(slice_key)
    by_row = {r["_row_index"]: r for r in rows}
    hidden_fields = [f for f in src.get("hidden", []) if f in (src.get("columns") or [])]

    seen: set[str] = set()
    over = {"512": 0, "1024": 0, "4096": 0}
    leaks = 0

    for case in cases:
        cid = case["case_id"]
        if cid in seen:
            hard.append(f"{slice_key}: duplicate case_id {cid}")
        seen.add(cid)

        q = case["question"]
        criteria = q.get("criteria")
        gold = case["gold"]

        # 2. gold reachable
        if case["task_type"] == "choice":
            if not isinstance(criteria, dict) or str(gold) not in criteria:
                hard.append(f"{slice_key}/{cid}: gold {gold!r} is not one of the option keys")
        elif case["task_type"] == "noul":
            if not isinstance(gold, bool):
                hard.append(f"{slice_key}/{cid}: noul gold {gold!r} is not a boolean")
        elif case["task_type"] == "score":
            if not isinstance(criteria, list) or not isinstance(gold, int) or not 0 <= gold < len(criteria):
                hard.append(f"{slice_key}/{cid}: score gold {gold!r} outside the level range")

        # 4. limits
        n_opts = len(criteria) if isinstance(criteria, (dict, list)) else 2
        if case["task_type"] == "choice" and n_opts > LIMIT_OPTIONS_DJEV:
            hard.append(f"{slice_key}/{cid}: {n_opts} options exceeds djev's {LIMIT_OPTIONS_DJEV}")
        if case["task_type"] == "choice" and n_opts > LIMIT_OPTIONS_LAYA:
            soft.append(f"{slice_key}: {n_opts} options exceeds Laya's HTTP guard of {LIMIT_OPTIONS_LAYA}")
        if case["task_type"] == "score" and not LIMIT_SCORE_LEVELS[0] <= n_opts <= LIMIT_SCORE_LEVELS[1]:
            hard.append(f"{slice_key}/{cid}: {n_opts} score levels outside {LIMIT_SCORE_LEVELS}")
        if len(str(q.get("instructions") or "")) > LIMIT_INSTRUCTIONS:
            hard.append(f"{slice_key}/{cid}: instructions exceed {LIMIT_INSTRUCTIONS} characters")
        if case["state_chars"] > LIMIT_STATE_CHARS:
            hard.append(f"{slice_key}/{cid}: state is {case['state_chars']} characters, over {LIMIT_STATE_CHARS}")
        if isinstance(criteria, dict):
            long_names = [k for k in criteria if len(k) > LIMIT_CRITERION_NAME]
            if long_names:
                hard.append(f"{slice_key}/{cid}: criterion name over {LIMIT_CRITERION_NAME} characters")

        # 3. leakage
        row = by_row.get(case["row_index"])
        if row is not None:
            blob = C.state_json(case["state"]).lower()
            presented = set()
            if isinstance(criteria, dict):
                presented = {str(v).strip().lower() for v in criteria.values()}
                presented |= {str(k).strip().lower() for k in criteria}
            for field in hidden_fields:
                value = row.get(field)
                texts = value if isinstance(value, list) else [value]
                for item in texts:
                    if not isinstance(item, str):
                        continue
                    probe = item.strip()
                    if not probe or probe.lower() in presented:
                        continue  # the gold option text legitimately appears as an option
                    threshold = MIN_RATIONALE_LEN if field in RATIONALE_FIELDS else MIN_LEAK_LEN
                    if len(probe) < threshold:
                        continue
                    needle = probe[:60].lower()
                    if needle in blob:
                        leaks += 1
                        hard.append(f"{slice_key}/{cid}: hidden field {field!r} appears in state")
                        break

        # 5. budget
        tokens = case["est_tokens"]
        for bound in (512, 1024, 4096):
            if tokens > bound:
                over[str(bound)] += 1

    # 6. preview
    previews = C.CASES / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    sample = cases[0]
    preview = {
        "note": "Exactly what would be POSTed for this case, with the key omitted. Content is untrusted data.",
        "case_id": sample["case_id"],
        "gold_withheld_from_request": sample["gold"],
        "request_body": {"model": C.JEV_MODEL, "state": sample["state"], "questions": {sample["question_key"]: sample["question"]}},
    }
    (previews / f"{slice_key}.json").write_text(json.dumps(preview, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    stats = {
        "cases": len(cases),
        "task_type": cases[0]["task_type"],
        "hidden_checked": len(hidden_fields),
        "leaks": leaks,
        "over_512": over["512"],
        "over_1024": over["1024"],
        "over_4096": over["4096"],
        "truncated": sum(1 for c in cases if c["truncated"]),
    }
    if verbose:
        print(f"    hidden fields checked: {hidden_fields}")
    return hard, soft, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], metavar="SLICE")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    keys = C.available_case_keys()
    if args.only:
        keys = [k for k in keys if k in set(args.only)]
    if not keys:
        print("No case files found. Run workspace/build_cases.py first.")
        return 2

    print(f"verifying {len(keys)} slice(s): " + ", ".join(keys))
    all_hard: list[str] = []
    all_soft: list[str] = []
    rows = []
    for key in keys:
        print(f"\n=== {key} ===")
        hard, soft, stats = check_slice(key, args.verbose)
        all_hard += hard
        all_soft += soft
        rows.append([
            key, stats["task_type"], stats["cases"], stats["hidden_checked"], stats["leaks"],
            stats["over_512"], stats["over_1024"], stats["over_4096"], stats["truncated"],
        ])
        print(f"    {stats['cases']:,} cases, {len(hard)} hard failure(s), {len(set(soft))} warning(s)")

    print()
    print(C.table(rows, ["slice", "type", "cases", "hidden fields", "leaks", ">512tok", ">1024tok", ">4096tok", "truncated"]))

    if all_soft:
        print("\nWarnings:")
        for msg in sorted(set(all_soft)):
            print(f"  - {msg}")

    print(f"\nKey check: {C.key_status()}")
    print(f"Request previews: {(C.CASES / 'previews').relative_to(C.ROOT)}/")

    if all_hard:
        print(f"\n{len(all_hard)} HARD FAILURE(S). Nothing should be sent until these are fixed:")
        for msg in all_hard[:40]:
            print(f"  - {msg}")
        if len(all_hard) > 40:
            print(f"  ... and {len(all_hard) - 40} more")
        return 1

    print("\nAll hard checks passed. Token counts above are 4-chars-per-token estimates, not API counts.")
    print("Next: uv run workspace/run_eval.py --dry-run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
