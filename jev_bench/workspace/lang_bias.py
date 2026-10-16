"""Why a model's accuracy moved in a language: per slice, accuracy and how often it says yes.

    uv run workspace/lang_bias.py --model or-cloudflare-clef --langs ta kn sw

For each slice, on the cases answered in English and in the language: accuracy,
the share of cases the model calls positive (p_true >= 0.5), the share whose
gold is positive, and the mean p_true. A drop that comes with a swing in the
positive rate is the model leaning one way on the language, not random errors.
Reads predictions only.
"""

from __future__ import annotations

import argparse
import json
import statistics

import common as C
from compare_langs import LANG_NAMES, SLICES, load
from score_runs import is_correct


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="label in models.json, e.g. or-cloudflare-clef")
    ap.add_argument("--langs", nargs="+", required=True)
    args = ap.parse_args()

    models = {m["label"]: m for m in json.loads((C.ROOT / "models.json").read_text(encoding="utf-8"))["models"]}
    m = models[args.model]
    en = load(m["run_id"])
    rows = []
    for lang in args.langs:
        xx = load(f"{m['label']}-{lang}")
        for key in SLICES:
            ids = [c for c in en if c in xx and en[c]["slice"] == key and en[c]["task_type"] == "noul"]
            if not ids:
                continue
            for name, recs in (("English", en), (LANG_NAMES[lang], xx)):
                rows.append([
                    key, name, len(ids),
                    f"{100 * statistics.fmean(is_correct(recs[c], 'noul') for c in ids):.1f}",
                    f"{100 * statistics.fmean(float(recs[c]['p_true']) >= 0.5 for c in ids):.1f}",
                    f"{100 * statistics.fmean(bool(recs[c]['gold']) for c in ids):.1f}",
                    f"{statistics.fmean(float(recs[c]['p_true']) for c in ids):.2f}",
                ])
    print(f"{m['name']}\n")
    print(C.table(rows, ["slice", "language", "cases", "accuracy", "says yes %", "gold yes %", "mean p_true"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
