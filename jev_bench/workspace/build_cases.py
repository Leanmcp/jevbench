"""Step 3a: turn downloaded rows into typed-decision cases.

Reads sources.json plus the downloaded files, samples deterministically, builds
each case's state and question from the `model_visible` allowlist only, and
writes one JSONL per slice to data/cases/.

    uv run workspace/build_cases.py                  # every text slice
    uv run workspace/build_cases.py --only medmcqa --only banking77
    uv run workspace/build_cases.py --permute        # add option-order variants
    uv run workspace/build_cases.py --n 50           # override target_n, for a cheap trial

No network, no model, no API key needed. Run verify_cases.py afterwards.
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics

import common as C

# Image slices run on djev only: Jev's route in this workspace has no image input
# and Laya takes text. They are NOT in DEFAULT_SLICES, so a plain build stays
# text-only and comparable across all three models. Build them with
# --with-images, or name one with --only.
IMAGE_SLICES = {"vqa_rad", "scienceqa_image"}

# Slices to build, in report order.
DEFAULT_SLICES = [
    "medmcqa",
    "medqa_usmle",
    "mmlu_pro",
    "banking77",
    "pubmedqa",
    "sst5",
    "scienceqa_text",
    "atbench500",
    "aegis2",
    "aegis2_response",
    "prompt_injections",
    "jailbreak_classification",
]

# Slices where permuting option order is meaningful.
PERMUTABLE = {"medmcqa", "medqa_usmle", "mmlu_pro", "banking77", "scienceqa_text"}

SEED = 20260926


def rows_for_slice(slice_key: str) -> tuple[list[dict], dict, dict]:
    """Return (rows, source_manifest_entry, extras)."""
    src = C.source_by_key(C.parent_key(slice_key))
    extras: dict = {}

    if slice_key in {"scienceqa_text", "scienceqa_image"}:
        want_image = slice_key == "scienceqa_image"
        cols = [c for c in src["columns"] if c != "image"]
        rows = C.load_rows(src, columns=cols)
        flags = C.scienceqa_has_image(C.local_path(src))
        if len(flags) != len(rows):
            raise RuntimeError(f"scienceqa image flags {len(flags)} != rows {len(rows)}")
        keep = [i for i, has_img in enumerate(flags) if has_img == want_image]
        extras["filtered_from"] = len(rows)
        extras["filter"] = f"image is {'not null' if want_image else 'null'}"
        rows = [dict(rows[i], _row_index=i) for i in keep]
        return rows, src, extras

    if slice_key == "vqa_rad":
        cols = [c for c in src["columns"] if c != "image"]
        rows = C.load_rows(src, columns=cols)
        before = len(rows)
        # Answers are free text. Only the closed-form yes/no subset gives a clean
        # noul; everything else is dropped and the count is reported.
        keep = [
            i for i, r in enumerate(rows)
            if str(r.get("answer", "")).strip().lower() in (C.VQA_YES | C.VQA_NO)
        ]
        extras["filtered_from"] = before
        extras["filter"] = "answer is closed-form yes/no"
        rows = [dict(rows[i], _row_index=i) for i in keep]
        return rows, src, extras

    all_rows = C.load_rows(src)
    rows = [dict(r, _row_index=i) for i, r in enumerate(all_rows)]

    if slice_key == "aegis2_response":
        before = len(rows)
        rows = [r for r in rows if r.get("response_label") in {"safe", "unsafe"} and r.get("response")]
        extras["filtered_from"] = before
        extras["filter"] = "response and response_label both present"
    elif slice_key == "banking77":
        extras["all_labels"] = sorted({str(r["label_text"]) for r in all_rows})
    return rows, src, extras


def build_slice(slice_key: str, permute: bool, n_override: int | None) -> list[dict]:
    rows, src, extras = rows_for_slice(slice_key)
    adapter = C.ADAPTERS[slice_key]
    stratify = src.get("stratify_by")
    if slice_key == "aegis2_response":
        stratify = "response_label"
    if slice_key in {"scienceqa_text", "scienceqa_image"}:
        stratify = "subject"
    if slice_key == "vqa_rad":
        stratify = "answer"

    target = n_override if n_override is not None else src.get("target_n")
    picks = C.stratified_sample(rows, target, SEED, stratify)

    # Image slices: extract the selected rows' images to files once, so cases.jsonl
    # holds a path rather than megabytes of base64 and the run is resumable
    # without rescanning a 122 MB parquet.
    image_paths: dict[int, str] = {}
    if slice_key in IMAGE_SLICES:
        wanted = [rows[p]["_row_index"] for p in picks]
        raw_images = C.read_images_at(C.local_path(src), wanted)
        missing = [i for i in wanted if i not in raw_images]
        if missing:
            print(f"    WARNING {len(missing)} selected rows had no image bytes; they are dropped")
        notes: list[dict] = []
        for idx, raw in raw_images.items():
            rel, note = C.write_image(C.parent_key(slice_key), idx, raw)
            image_paths[idx] = rel
            notes.append(note)
        resized = sum(1 for n in notes if "resized_to" in n)
        recompressed = sum(1 for n in notes if "recompressed_jpeg_quality" in n)
        total_bytes = sum(n.get("final_bytes", n["original_bytes"]) for n in notes)
        print(f"    extracted {len(image_paths)} images, {total_bytes:,} bytes total"
              f" ({resized} resized to fit {C.MAX_IMAGE_SIDE}px, {recompressed} recompressed)")

    cases: list[dict] = []
    for pick in picks:
        row = rows[pick]
        row_index = row["_row_index"]
        if slice_key in IMAGE_SLICES and row_index not in image_paths:
            continue
        family_id = f"{slice_key}-{row_index}"
        perturbations = ["none"]
        if permute and slice_key in PERMUTABLE:
            perturbations.append("permuted")

        for perturbation in perturbations:
            kwargs = {}
            if slice_key == "banking77":
                kwargs["all_labels"] = extras["all_labels"]
            order = None
            if perturbation == "permuted":
                probe = adapter(row, None, **kwargs)
                order = C.permuted_order(len(probe["option_texts"]), SEED + row_index)
                if order == list(range(len(order))):  # a no-op shuffle is not a variant
                    order = list(reversed(order))
            built = adapter(row, order, **kwargs)

            state, truncated, chars = C.truncate_state(built["state"])
            criteria = built["question"].get("criteria")
            if isinstance(criteria, dict):
                n_options = len(criteria)
            elif isinstance(criteria, list):
                n_options = len(criteria)
            else:
                n_options = 2

            cases.append(
                {
                    "case_id": f"{family_id}-{perturbation}",
                    "family_id": family_id,
                    "source": C.parent_key(slice_key),
                    "slice": slice_key,
                    "row_index": row_index,
                    "task_type": built["question"]["type"],
                    "question_key": "decision",
                    "state": state,
                    "question": built["question"],
                    "gold": built["gold"],
                    "n_options": n_options,
                    "option_order": built["order"],
                    "perturbation": perturbation,
                    "truncated": truncated,
                    "state_chars": chars,
                    "est_tokens": C.est_tokens(chars + len(C.state_json(built["question"]))),
                    "state_hash": C.content_hash(C.state_json(state)),
                    "image_path": image_paths.get(row_index),
                    "license": src["license"],
                    "redistributable": src.get("redistributable", False),
                    "exposure": src["exposure"],
                    "hf_repo": src["hf_repo"],
                    "revision": src["revision"],
                }
            )
    if extras.get("filter"):
        print(f"    filter: {extras['filter']} kept {len(rows):,} of {extras['filtered_from']:,} rows")
    return cases


def summarise(slice_key: str, cases: list[dict]) -> list:
    toks = [c["est_tokens"] for c in cases]
    golds = collections.Counter(str(c["gold"]) for c in cases)
    opts = sorted({c["n_options"] for c in cases})
    return [
        slice_key,
        cases[0]["task_type"],
        len(cases),
        len({c["family_id"] for c in cases}),
        f"{opts[0]}-{opts[-1]}" if len(opts) > 1 else str(opts[0]),
        len(golds),
        f"{min(toks)}/{int(statistics.median(toks))}/{max(toks)}",
        sum(1 for c in cases if c["truncated"]),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], metavar="SLICE")
    ap.add_argument("--skip", action="append", default=[], metavar="SLICE")
    ap.add_argument("--permute", action="store_true", help="add an option-order variant per case, doubling permutable slices")
    ap.add_argument("--n", type=int, default=None, help="override target_n for every slice")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--with-images", action="store_true",
                    help="also build the djev-only image slices (vqa_rad, scienceqa_image)")
    args = ap.parse_args()

    catalogue = DEFAULT_SLICES + (sorted(IMAGE_SLICES) if args.with_images else [])
    if args.only:
        catalogue = DEFAULT_SLICES + sorted(IMAGE_SLICES)
    slices = [s for s in catalogue if (not args.only or s in set(args.only)) and s not in set(args.skip)]
    if args.list:
        print("buildable slices: " + ", ".join(DEFAULT_SLICES))
        print("permutable:       " + ", ".join(sorted(PERMUTABLE)))
        print("not built here:   vqa_rad (needs djev image input)")
        return 0
    if not slices:
        print("nothing selected. known slices: " + ", ".join(DEFAULT_SLICES))
        return 2

    print(f"seed={SEED}  permute={args.permute}  n_override={args.n}")
    rows_out = []
    for slice_key in slices:
        print(f"\n=== {slice_key} ===")
        cases = build_slice(slice_key, args.permute, args.n)
        path = C.write_cases(slice_key, cases)
        print(f"    wrote {len(cases):,} cases to {path.relative_to(C.ROOT)}")
        rows_out.append(summarise(slice_key, cases))

    print()
    print(C.table(rows_out, ["slice", "type", "cases", "families", "options", "gold classes", "est tokens min/med/max", "truncated"]))
    total = sum(r[2] for r in rows_out)
    print(f"\n{total:,} cases across {len(rows_out)} slices. That is {total:,} API requests at one question per request.")
    print("Next: uv run workspace/verify_cases.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
