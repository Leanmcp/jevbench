"""User-run English Laya smoke check; downloads one checkpoint on first load."""

import argparse
import json
import statistics
import time

import torch
import laya
from laya.revisions import PINNED_REVISIONS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=("cpu", "mps", "cuda"), default="cpu")
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    if args.device == "mps" and not torch.backends.mps.is_available():
        parser.error("PyTorch MPS is unavailable; try --device cpu")
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("PyTorch CUDA is unavailable; try --device cpu")

    model_id = "convaiinnovations/laya"
    started = time.perf_counter()
    model = laya.load(model_id, device=args.device, revision=PINNED_REVISIONS[model_id])
    print(json.dumps({
        "model": model_id,
        "revision": model.revision,
        "device": str(model.device),
        "load_seconds_including_any_download": round(time.perf_counter() - started, 3),
    }, indent=2))

    questions = {
        "department": {
            "type": "choice",
            "instructions": "Which department should handle this message?",
            "criteria": {
                "billing": "Charges, invoices, payments, or refunds",
                "technical": "Software crashes, errors, or outages",
                "sales": "Pricing information or a new purchase",
            },
        },
        "refund": {
            "type": "noul",
            "instructions": "Does the customer explicitly request a refund?",
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is the issue described?",
            "criteria": ["Routine, no deadline", "Time-sensitive", "Service blocked now"],
        },
    }
    cases = [
        ("I was charged twice. Please refund the duplicate payment.", "billing", True),
        ("The application crashes on startup. Please fix it; I am not asking for a refund.", "technical", False),
        ("Please send the pricing for a new team subscription.", "sales", False),
    ]
    for state, department, refund in cases:
        result = model.predict(state, questions)
        answers = result["answers"]
        print(json.dumps({
            "state": state,
            "expected_department": department,
            "expected_refund": refund,
            "department_correct": answers["department"]["choice"] == department,
            "refund_correct_at_0_5": (answers["refund"]["noul"] >= 0.5) == refund,
            "result": result,
        }, indent=2))

    def sync():
        if model.device.type == "mps":
            torch.mps.synchronize()
        elif model.device.type == "cuda":
            torch.cuda.synchronize(model.device)

    for selected in ({"department": questions["department"]}, questions):
        model.predict(cases[0][0], selected)
        samples = []
        for _ in range(args.repeats):
            sync()
            started = time.perf_counter()
            model.predict(cases[0][0], selected)
            sync()
            samples.append(time.perf_counter() - started)
        print(json.dumps({
            "questions_per_call": len(selected),
            "repeats": args.repeats,
            "median_warm_ms": round(statistics.median(samples) * 1000, 2),
            "serial_questions_per_second": round(len(selected) * len(samples) / sum(samples), 2),
            "device_after_run": str(model.device),
        }, indent=2))


if __name__ == "__main__":
    main()
