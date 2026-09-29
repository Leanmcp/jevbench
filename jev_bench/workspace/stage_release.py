"""Stage the public JevBench release into jev_bench/release/.

Copies only what the paper says is released, and nothing else:

  cases/        built cases for every slice. Rows whose source is not
                redistributable (SST-5) keep their identifiers, gold label and
                state_hash, but their state text is removed.
  images/       the ScienceQA (CC-BY-SA-4.0) and VQA-RAD (CC0-1.0) images the
                image cases point to.
  predictions/  one folder per system: predictions.jsonl, meta.json, scores.json.
                Retried cases are de-duplicated with the scorer's rule (the last
                record for a case_id wins), so each file holds one decision per case.
  analysis/     paired_bootstrap.json and the djev image ablation.
  provenance/   djev serving provenance (vLLM command, container logs, config).
  sources.json, MANIFEST.measured.json, README.md, LICENSE.md

Excluded on purpose: the harness code (it lives on GitHub, CODE_URL below),
raw downloaded dataset copies (re-download them from the pinned revisions),
trial and smoke runs, runs of models not in the paper, and raw request logs.

The script checks its own output: no prediction may carry state text, the SST-5
cases may carry no sentence, and the decision total must equal EXPECTED_TOTAL.
It exits non-zero if any check fails, so a failed stage cannot be uploaded by
accident.

Run from the jev_bench/ directory:
    time uv run workspace/stage_release.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # jev_bench/
DATA = ROOT / "data"
OUT = ROOT / "release"

# run folder under data/runs  ->  published folder name under predictions/
RUNS = {
    "jev-1.13.0-20260926T133639": "jev-1.13.0",
    "djev-full": "djev-0.1",
    "laya-en-full": "laya-421m-en",
    "djev-multimodal": "djev-0.1-images",
}
EXPECTED_TOTAL = 24_799  # unique decisions reported in the paper

# Where the harness code is published. The dataset card links here.
CODE_URL = "https://github.com/rosaboyle/jev-benchmark"
PROVENANCE_SKIP_PREFIXES = ("clm", "inspect-clm", "logs-clm")
TEXT_KEYS = ("state",)  # fields that carry source text


def fail(msg: str) -> None:
    print(f"CHECK FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def stage_cases() -> None:
    redacted = 0
    for src in sorted((DATA / "cases").glob("*.jsonl")):
        rows = read_jsonl(src)
        for row in rows:
            if row.get("redistributable") is False:
                row.pop("state", None)
                row["state_withheld"] = "source licence does not permit redistribution; see state_hash"
                redacted += 1
        write_jsonl(OUT / "cases" / src.name, rows)
    sst = read_jsonl(OUT / "cases" / "sst5.jsonl")
    if any("state" in r for r in sst):
        fail("SST-5 cases still carry state text")
    if not all(r.get("state_hash") for r in sst):
        fail("an SST-5 case has no state_hash")
    print(f"cases: {len(list((OUT / 'cases').glob('*.jsonl')))} files, {redacted} rows redacted")


def stage_images() -> None:
    for sub in ("scienceqa", "vqa_rad"):
        shutil.copytree(DATA / "images" / sub, OUT / "images" / sub)
    print("images: scienceqa, vqa_rad")


def stage_predictions() -> int:
    total = 0
    for run, name in RUNS.items():
        src = DATA / "runs" / run
        last: dict[str, dict] = {}
        for row in read_jsonl(src / "predictions.jsonl"):
            last[row["case_id"]] = row  # last record wins, as in score_runs.py
        rows = list(last.values())
        for row in rows:
            for key in TEXT_KEYS:
                if key in row:
                    fail(f"{run}: prediction {row['case_id']} carries '{key}'")
        write_jsonl(OUT / "predictions" / name / "predictions.jsonl", rows)
        for extra in ("meta.json", "scores.json"):
            if (src / extra).exists():
                shutil.copy2(src / extra, OUT / "predictions" / name / extra)
        print(f"predictions/{name}: {len(rows)} decisions")
        total += len(rows)
    if total != EXPECTED_TOTAL:
        fail(f"decision total is {total}, expected {EXPECTED_TOTAL}")
    return total


def stage_analysis() -> None:
    (OUT / "analysis").mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA / "runs" / "paired_bootstrap.json", OUT / "analysis" / "paired_bootstrap.json")
    shutil.copy2(DATA / "runs" / "djev-image-ablation" / "image_ablation.json",
                 OUT / "analysis" / "image_ablation.json")


def stage_provenance() -> None:
    dst = OUT / "provenance" / "djev"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted((ROOT / "provenance" / "vm").iterdir()):
        if f.is_file() and not f.name.startswith(PROVENANCE_SKIP_PREFIXES):
            shutil.copy2(f, dst / f.name)


def stage_manifests() -> None:
    shutil.copy2(ROOT / "sources.json", OUT / "sources.json")
    shutil.copy2(DATA / "MANIFEST.measured.json", OUT / "MANIFEST.measured.json")


README = """---
pretty_name: JevBench
license: other
license_name: per-source
license_link: LICENSE.md
language:
- en
tags:
- evaluation
- calibration
- typed-decisions
- benchmark
size_categories:
- 10K<n<100K
---

# JevBench

Cases and predictions for *JevBench: An Open Evaluation Framework for Typed
Decision Models*. The evaluation code is on GitHub: {code_url} JevBench evaluates models that return typed decisions
(a yes/no probability, a distribution over a set of choices, or an expected
level on an ordered rubric) on identical inputs built from public datasets.

## Contents

| Path | What it holds |
|---|---|
| `cases/` | One JSONL file per slice. Each row is the exact request sent to every model, plus the gold answer, source revision and licence. |
| `images/` | Images for the ScienceQA and VQA-RAD image slices. |
| `predictions/<system>/predictions.jsonl` | One decision per case with the full probability vector, latency and token counts. No source text. |
| `analysis/` | Paired bootstrap results and the djev image ablation. |
| `provenance/djev/` | Serving provenance for djev-0.1 (vLLM command line, container logs, configuration). |
| `sources.json` | Every source dataset pinned to a Hugging Face revision, with the fields sent and withheld. |

Systems: `jev-1.13.0` (hosted commercial model), `djev-0.1` (open, DiffusionGemma
26B-A4B backbone; `djev-0.1-images` holds its image slices), `laya-421m-en`
(open, ModernBERT-large encoder). Total: {total} decisions.

## Licences

Each case row carries the licence of its source dataset in its `license` field;
licences do not merge across sources. SST-5 states no licence on its card, so
its cases are released without their sentence text: `state_hash` identifies each
sentence, which can be recovered from the pinned source revision in
`sources.json`.

## Code

The harness that downloads the sources, builds and verifies these cases, runs
models and scores them is released under the MIT Licence at {code_url}. Each
`predictions/<system>/scores.json` holds the scores reported in the paper.
"""

LICENSE = """# Licences

The cases and images in this dataset are derived from the datasets below and
keep their original licences; see `sources.json` for the pinned revisions. The
predictions, analysis files and provenance are released under the MIT Licence,
Copyright (c) 2026 Leanmcp, as is the evaluation code published on GitHub.

| Source | Licence |
|---|---|
| MedMCQA | Apache-2.0 |
| MedQA-USMLE (4 options) | CC-BY-4.0 |
| MMLU-Pro | MIT |
| PubMedQA | MIT |
| ScienceQA | CC-BY-SA-4.0 |
| BANKING77 (via mteb/banking77; upstream PolyAI, CC-BY-4.0) | MIT / CC-BY-4.0 |
| SST-5 | not stated; text not redistributed |
| ATBench | Apache-2.0 |
| Aegis 2.0 | CC-BY-4.0 |
| deepset prompt-injections | Apache-2.0 |
| jailbreak-classification | Apache-2.0 |
| VQA-RAD | CC0-1.0 |
"""


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    stage_cases()
    stage_images()
    total = stage_predictions()
    stage_analysis()
    stage_provenance()
    stage_manifests()
    readme = README.replace("{total}", f"{total:,}").replace("{code_url}", CODE_URL)
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    (OUT / "LICENSE.md").write_text(LICENSE, encoding="utf-8")
    print(f"\nStaged {total:,} decisions into {OUT}")
    print("All checks passed. Review README.md and LICENSE.md before uploading.")


if __name__ == "__main__":
    main()
