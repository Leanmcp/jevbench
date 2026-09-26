"""Step 3c: send the cases and record what came back.

    # always do this first: builds every request, sends nothing
    uv run workspace/run_eval.py --dry-run

    # a cheap real trial before the full run
    uv run workspace/run_eval.py --only prompt_injections --limit 20

    # the full run
    time uv run workspace/run_eval.py --concurrency 4

    # a local djev instead of the Jev API
    uv run workspace/run_eval.py --endpoint djev --model djev-0.1

One question per request, so one row of predictions per case. Question batching
is a separate experiment and would change the latency numbers, so it is not
mixed in here.

Resumable: re-running the same --run-id skips case ids already recorded. The
API key is read from TYPESAFE_API_KEY, never logged, and scrubbed out of any
error text before it is written to disk.

Predictions store the decision, the probability vector, latency and token usage,
but never the state text. The cases file already holds that, which keeps this
file publishable even for slices whose source text cannot be redistributed.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import threading
import time

import common as C

STOP_AFTER_CONSECUTIVE_FAILURES = 15


def resolve_endpoint(name: str) -> str:
    if name == "jev":
        return C.JEV_URL
    if name == "djev":
        return C.DJEV_URL
    if name.startswith("http"):
        return name
    raise SystemExit(f"--endpoint must be 'jev', 'djev' or a URL, got {name!r}")


def load_done(path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    for rec in C.read_jsonl(path):
        if rec.get("error") is None:
            done.add(rec["case_id"])
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], metavar="SLICE")
    ap.add_argument("--skip", action="append", default=[], metavar="SLICE")
    ap.add_argument("--endpoint", default="jev", help="jev, djev, or a full URL")
    ap.add_argument("--model", default=C.JEV_MODEL)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--limit", type=int, default=None, help="cap cases per slice")
    ap.add_argument("--concurrency", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--stop-after", type=int, default=STOP_AFTER_CONSECUTIVE_FAILURES, help="abort after this many consecutive failures")
    ap.add_argument("--dry-run", action="store_true", help="build every request, send nothing")
    ap.add_argument("--no-send-model", action="store_true",
                    help="omit the model field from the request body. djev's documented contract is state/questions/options only.")
    ap.add_argument("--label", default=None,
                    help="what to record as the model in meta.json, when it differs from what is sent (e.g. djev-0.1)")
    ap.add_argument("--seed", type=int, default=None, help="djev options.seed. Pass 0 for a reproducible run.")
    ap.add_argument("--samples", type=int, default=None, help="djev options.samples, 1-4. Averages independent one-step reads.")
    args = ap.parse_args()

    options: dict = {}
    if args.seed is not None:
        options["seed"] = args.seed
    if args.samples is not None:
        options["samples"] = args.samples
    label = args.label or args.model or "unlabelled"

    keys = C.available_case_keys()
    if args.only:
        keys = [k for k in keys if k in set(args.only)]
    keys = [k for k in keys if k not in set(args.skip)]
    if not keys:
        print("No case files selected. Run workspace/build_cases.py first.")
        return 2

    endpoint = resolve_endpoint(args.endpoint)
    status = C.key_status()
    print(f"endpoint  {endpoint}")
    print(f"model     sent={'(omitted)' if args.no_send_model else args.model}  recorded as={label}")
    print(f"options   {options or '(none)'}")
    print(f"api key   {status['env_var']} present={status['present']} length={status['length']}")

    client = C.DecisionClient(
        endpoint=endpoint,
        model=None if args.no_send_model else args.model,
        options=options or None,
        require_key=(not args.dry_run) and endpoint.startswith("https://api.typesafe.ai"),
        timeout=args.timeout,
    )

    work: list[dict] = []
    for key in keys:
        cases = C.read_cases(key)
        if args.limit:
            cases = cases[: args.limit]
        work += cases
    print(f"slices    {len(keys)}: " + ", ".join(keys))
    print(f"cases     {len(work):,}")

    if args.dry_run:
        sizes = []
        for case in work:
            body = json.dumps(client.build_request(C.attach_images(case)), ensure_ascii=False)
            sizes.append(len(body.encode("utf-8")))
        sizes.sort()
        print(f"\nBuilt {len(sizes):,} request bodies without sending any.")
        print(f"body bytes  min={sizes[0]:,}  median={sizes[len(sizes)//2]:,}  max={sizes[-1]:,}  total={sum(sizes):,}")
        print("\nCheck one rendered request in data/cases/previews/ then drop --dry-run.")
        return 0

    run_id = args.run_id or f"{label}-{time.strftime('%Y%m%dT%H%M%S')}"
    run_dir = C.RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    pred_path = run_dir / "predictions.jsonl"
    done = load_done(pred_path)
    todo = [c for c in work if c["case_id"] not in done]
    print(f"run id    {run_id}")
    print(f"resuming  {len(done):,} already recorded, {len(todo):,} to send\n")
    if not todo:
        print("Nothing left to send. Next: uv run workspace/score_runs.py --run-id " + run_id)
        return 0

    meta_path = run_dir / "meta.json"
    prior_meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "first_started_at": prior_meta.get("first_started_at") or prior_meta.get("started_at") or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "resume_count": prior_meta.get("resume_count", -1) + 1,
                "endpoint": endpoint,
                "model_requested": label,
                "model_sent_on_wire": None if args.no_send_model else args.model,
                "request_options": options or None,
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "slices": keys,
                "n_cases_total": len(work),
                "concurrency": args.concurrency,
                "limit_per_slice": args.limit,
                "api_key_env": status["env_var"],
                "api_key_present": status["present"],
                "one_question_per_request": True,
                "manifest_pinned_on": C.load_manifest()["pinned_on"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lock = threading.Lock()
    state = {"done": 0, "errors": 0, "consecutive": 0, "stop": False, "t0": time.time()}

    def handle(case: dict) -> dict:
        if state["stop"]:
            return {}
        result = client.call(C.attach_images(case))
        rec = {
            "run_id": run_id,
            "case_id": case["case_id"],
            "family_id": case["family_id"],
            "slice": case["slice"],
            "source": case["source"],
            "task_type": case["task_type"],
            "perturbation": case["perturbation"],
            "n_options": case["n_options"],
            "gold": case["gold"],
            "truncated_state": case["truncated"],
            "latency_ms": result.get("latency_ms"),
            "attempts": result.get("attempts"),
            "error": None if result["ok"] else result["error"],
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        if result["ok"]:
            payload = result["response"]
            rec.update(C.parse_answer(payload, case["question_key"], case["task_type"]))
            rec.update(C.usage_of(payload))
        with lock:
            C.jsonl_append(pred_path, [rec])
            state["done"] += 1
            if rec["error"] or rec.get("parse_error"):
                state["errors"] += 1
                state["consecutive"] += 1
                if state["consecutive"] >= args.stop_after:
                    state["stop"] = True
                    print(f"\nStopping: {state['consecutive']} consecutive failures. Last: {rec.get('error') or rec.get('parse_error')}")
            else:
                state["consecutive"] = 0
            if state["done"] % 25 == 0 or state["done"] == len(todo):
                rate = state["done"] / max(time.time() - state["t0"], 1e-6)
                left = (len(todo) - state["done"]) / rate if rate else 0
                print(f"  {state['done']:,}/{len(todo):,}  errors={state['errors']}  {rate:.1f}/s  eta {left/60:.1f} min")
        return rec

    with cf.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        list(pool.map(handle, todo))

    elapsed = time.time() - state["t0"]
    recs = C.read_jsonl(pred_path)
    lat = sorted(r["latency_ms"] for r in recs if r.get("latency_ms"))
    toks = [r.get("input_tokens") or 0 for r in recs if r.get("input_tokens")]
    print(f"\nwrote {pred_path.relative_to(C.ROOT)}  ({len(recs):,} records)")
    print(f"elapsed {elapsed/60:.1f} min, {state['errors']} error(s)")
    if lat:
        def pct(p):
            return lat[min(len(lat) - 1, int(len(lat) * p))]
        print(f"latency ms  p50={pct(0.5):.0f}  p95={pct(0.95):.0f}  p99={pct(0.99):.0f}  max={lat[-1]:.0f}")
    if toks:
        print(f"input tokens reported by the API: total={sum(toks):,}  mean={sum(toks)/len(toks):.0f}")
    print(f"\nNext: uv run workspace/score_runs.py --run-id {run_id}")
    return 1 if state["stop"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
