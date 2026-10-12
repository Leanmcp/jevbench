<p align="center">
  <img src="assets/jevbench-logo.svg" alt="JevBench" width="560">
</p>

<h3 align="center">JevBench: an open framework for benchmarking typed decision models</h3>

<p align="center">
  <a href="https://www.preprints.org/manuscript/202610.0181"><img alt="Paper" src="https://img.shields.io/badge/paper-Preprints.org-b31b1b"></a>
  <a href="https://www.preprints.org/frontend/manuscript/da3d1f1f93bf32fe4a28e70c6168ef87/download_pub"><img alt="PDF" src="https://img.shields.io/badge/PDF-download-informational"></a>
  <a href="https://huggingface.co/datasets/Leanmcp/jevbench"><img alt="Dataset on Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20dataset-Leanmcp%2Fjevbench-ffcc4d"></a>
  <a href="LICENSE"><img alt="Licence: MIT" src="https://img.shields.io/badge/licence-MIT-green"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-3776ab">
  <a href="https://docs.astral.sh/uv/"><img alt="uv" src="https://img.shields.io/badge/built%20with-uv-de5fe9"></a>
</p>

<p align="center">
  <a href="https://www.preprints.org/manuscript/202610.0181">Paper</a> ·
  <a href="https://www.preprints.org/frontend/manuscript/da3d1f1f93bf32fe4a28e70c6168ef87/download_pub">PDF</a> ·
  <a href="https://leanmcp.github.io/jevbench/">Website</a> ·
  <a href="https://huggingface.co/datasets/Leanmcp/jevbench">Dataset</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="SECURITY.md">Security</a>
</p>

## Results

<!-- results:start -->
### JevBench Index

One number per model: every dataset on 0-100, averaged within six clusters, then the six clusters averaged. Datasets not run yet are left out: (4/6) means the score covers four of the six clusters, and * that a cluster is missing a dataset. ‡ the model's API rejects some datasets outright (too many options, or question types it does not take); those count as 0.

| # | Model | **Index** | Science | Tool calling | Business | Selection | Ranking | Judging |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | pplx-decider v1.1 | **78.0** | 80.4 | 89.1 | 84.6 | 84.3 | 56.9 | 72.8 |
| 2 | Liquid D1 | **77.4** (5/6) | 79.2 | 84.0 | 86.5 | 82.4 | – | 54.7 |
| 3 | Mercury Decide | **76.6** | 76.4 | 89.3 | 89.0 | 81.6 | 55.9 | 67.4 |
| 4 | Jev 1.13 | **76.5** | 82.5 | 86.8 | 84.3 | 85.6 | 56.4 | 63.7 |
| 5 | Clef | **76.1** | 77.1 | 87.6 | 90.7 | 86.6 | 55.9 | 59.0 |
| 6 | Microsoft Decision 1 | **75.6** | 76.5 | 85.9 | 86.4 | 84.2 | 54.9 | 65.8 |
| 7 | GPT-6 Luna Decisions | **73.4** | 76.3 | 86.4 | 82.5 | 79.1 | 54.8 | 61.1 |
| 8 | djev-0.1 | **73.1** (3/6) | 62.8 | – | 78.9 | 77.4 | – | – |
| 9 | Clef-omni | **72.0** | 76.6 | 81.2 | 90.9 | 79.1 | 53.9 | 50.2 |
| 10 | Clef-flash | **71.8** | 75.3 | 81.9 | 91.4 | 78.5 | 54.3 | 49.2 |
| 11 | Kev 4B | **66.8** (5/6) | 65.6 | 76.1 | 85.9 | 73.2 | – | 33.3 |
| 12 | Drex v1.5 | **66.2*** | 71.8 | 81.4 | 85.5 | 75.2 | 37.3 | 46.0 |
| 13 | Solar Decide | **60.3**‡ | 76.7 | 60.6 | 42.5 | 79.4 | 44.0 | 58.7 |
| 14 | TEv1 4B (exp.) | **56.9**‡ | 66.7 | 58.4 | 43.5 | 69.0 | 54.7 | 49.0 |
| 15 | Solar Decide Flash | **55.1**‡ | 64.2 | 52.0 | 41.0 | 74.4 | 49.5 | 49.3 |
| 16 | Laya 421M | **52.4** (3/6) | 30.3 | – | 57.5 | 69.3 | – | – |
| 17 | Span-01 | **12.2**‡* | 0.0 | 0.0 | 0.0 | 73.1 | 0.0 | 0.0 |

### Every dataset

Every model on every dataset, from the scored runs on 2026-10-11. Accuracy in %, except where the row says otherwise; ranking rows are nDCG@10 on a fixed BM25 top-20, with BM25's own score in the label. Bold is the best on each row.

| Dataset | n | Jev 1.13 | Liquid D1 | djev | Laya | Clef | Clef-flash | Clef-omni | pplx v1.1 | GPT-6 Luna | MS Decision 1 | Solar | Solar Flash | Drex | Mercury | TEv1 4B | Kev 4B | Span-01 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Safety** | | | | | | | | | | | | | | | | | | |
| [Aegis 2.0 prompts](https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-2.0) | 500 | 82.8 | **86.6** | 81.0 | 54.2 | 83.2 | 83.2 | 84.8 | 86.0 | 74.8 | 82.0 | 80.8 | 73.6 | 79.2 | 84.0 | 76.8 | 84.0 | 81.8 |
| [Aegis 2.0 responses](https://huggingface.co/datasets/nvidia/Aegis-AI-Content-Safety-Dataset-2.0) | 500 | 81.2 | 78.8 | 69.2 | 52.8 | 78.6 | 79.0 | 79.0 | 80.8 | 72.6 | **82.2** | 75.4 | 72.0 | 72.8 | 77.2 | 67.8 | 79.4 | 74.8 |
| [ATBench](https://huggingface.co/datasets/AI45Research/ATBench) | 500 | 93.0 | 78.6 | 75.8 | 65.4 | **93.8** | 76.8 | 67.4 | 74.6 | 87.8 | 86.8 | 73.8 | 50.0 | 77.0 | 68.8 | 53.6 | 48.6 | 62.8 |
| [Jailbreak classification](https://huggingface.co/datasets/jackhhao/jailbreak-classification) | 400 | **97.5** | 96.5 | 96.5 | 93.0 | 97.0 | 94.2 | 92.5 | 89.8 | 96.8 | 96.5 | 96.5 | 97.0 | 92.0 | 96.8 | 91.7 | 94.8 | – |
| [Prompt injections](https://huggingface.co/datasets/deepset/prompt-injections) | 116 | 73.3 | 71.6 | 64.7 | 81.0 | 80.2 | 59.5 | 71.6 | **90.5** | 63.8 | 73.3 | 70.7 | 79.3 | 55.2 | 81.0 | 55.2 | 59.5 | – |
| **Medicine** | | | | | | | | | | | | | | | | | | |
| [MedMCQA](https://huggingface.co/datasets/openlifescienceai/medmcqa) | 1,000 | **78.1** | 77.0 | 53.8 | 26.9 | 72.5 | 70.4 | 72.5 | 75.7 | 77.3* | 75.9 | 72.2 | 63.4 | 66.6 | 72.6 | 61.0 | 56.4 | – |
| [MedQA-USMLE](https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options) | 1,000 | 87.3 | 86.6 | 71.2 | 26.1 | 84.3 | 76.6 | 79.5 | **88.9** | 87.6 | 80.7 | 83.1 | 72.2 | 75.5 | 84.9 | 68.9 | 67.2 | – |
| [PubMedQA](https://huggingface.co/datasets/qiaojin/PubMedQA) | 500 | **70.6** | 70.4 | 62.2 | 32.8 | 67.8 | 69.6 | 67.4 | 69.6 | 62.8 | 68.0 | 59.4 | 52.4 | 65.2 | 65.6 | 66.8 | 64.6 | – |
| **Exams** | | | | | | | | | | | | | | | | | | |
| [MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) | 1,000 | **80.6** | 66.4 | 42.3 | 12.5 | 66.8 | 67.6 | 71.5 | 70.8 | 59.9 | 64.7 | 72.5 | 47.2 | 61.0 | 64.5 | 48.4 | 52.7 | – |
| [ScienceQA](https://huggingface.co/datasets/derek-thomas/ScienceQA) | 1,000 | 95.7 | 95.8 | 84.7 | 53.4 | 93.9 | 92.3 | 92.1 | **97.0** | 94.1 | 93.2 | 96.2 | 85.6 | 90.6 | 94.2 | 88.5 | 86.9 | – |
| **Language** | | | | | | | | | | | | | | | | | | |
| [BANKING77](https://huggingface.co/datasets/mteb/banking77) | 1,000 | 81.3 | 85.7 | 71.4 | 36.3 | 94.8 | **96.1** | 94.8 | 81.8 | 78.6 | 86.4 | – | – | 84.9 | 89.9 | – | 85.3 | – |
| [SST-5](https://huggingface.co/datasets/SetFit/sst5), MAE ↓ | 500 | 0.51 | 0.51 | 0.54 | 0.85 | 0.54 | 0.53 | 0.52 | 0.51 | 0.54 | 0.54 | 0.60 | 0.72 | 0.56 | **0.48** | 0.52 | 0.54 | – |
| **Tools** | | | | | | | | | | | | | | | | | | |
| [MCP-Bench routing](https://github.com/Accenture/mcp-bench) | 112 | 95.5 | 90.2 | – | – | 95.5 | 87.5 | 85.7 | 98.2 | 96.3* | 94.6 | – | – | 92.9 | **100.0** | – | 81.2 | – |
| [MCP-Bench tools](https://github.com/Accenture/mcp-bench) | 26 | **100.0** | **100.0** | – | – | **100.0** | 92.3 | 92.3 | **100.0** | **100.0** | **100.0** | **100.0** | 73.1 | **100.0** | **100.0** | 88.5 | 73.1 | – |
| [MCPMark routing](https://github.com/eval-sys/mcpmark) | 338 | 51.5 | 45.9 | – | – | 55.0 | 47.6 | 46.7 | **58.0** | 49.1* | 48.8 | 47.9 | 40.5 | 32.8 | 57.1 | 45.0 | 50.0 | – |
| [MCPMark tools](https://github.com/eval-sys/mcpmark) | 18 | **100.0** | **100.0** | – | – | **100.0** | **100.0** | **100.0** | **100.0** | **100.0** | **100.0** | 94.4 | 94.4 | **100.0** | **100.0** | **100.0** | **100.0** | – |
| **Ranking** | | | | | | | | | | | | | | | | | | |
| [NFCorpus, all at once](https://huggingface.co/datasets/BeIR/nfcorpus) (BM25 0.332) | 298 | 0.361 | – | – | – | 0.371* | 0.366* | 0.357* | 0.366 | 0.356* | 0.364* | 0.305* | 0.304* | **0.371** | 0.355 | 0.357* | 0.352 | – |
| [NFCorpus, graded](https://huggingface.co/datasets/BeIR/nfcorpus) (BM25 0.332) | 4,924 | 0.377 | – | – | – | 0.376 | 0.379 | **0.380** | 0.378 | 0.365 | 0.373 | 0.354 | 0.364 | 0.375 | 0.367 | 0.354 | 0.305 | – |
| [NFCorpus, per document](https://huggingface.co/datasets/BeIR/nfcorpus) (BM25 0.332) | 298 | 0.378 | – | – | – | 0.373 | 0.369 | 0.361 | **0.381** | 0.368 | 0.368 | 0.324 | 0.330 | 0.373 | 0.375 | 0.361 | – | – |
| [SciFact, all at once](https://huggingface.co/datasets/BeIR/scifact) (BM25 0.661) | 300 | 0.739 | – | – | – | 0.752 | 0.738 | 0.723 | **0.753** | 0.749* | 0.737 | 0.630 | 0.637 | – | 0.726 | 0.722 | – | – |
| [SciFact, per document](https://huggingface.co/datasets/BeIR/scifact) (BM25 0.661) | 300 | 0.750 | – | – | – | 0.745 | 0.717 | 0.716 | **0.756** | 0.729 | 0.730 | 0.557 | 0.660 | – | 0.743 | 0.733 | – | – |
| **Judging** | | | | | | | | | | | | | | | | | | |
| [HelpSteer2](https://huggingface.co/datasets/nvidia/HelpSteer2), Spearman | 500 | 0.482 | 0.547† | – | – | 0.510 | 0.384 | 0.444 | **0.641** | 0.492 | 0.566 | 0.423 | 0.354 | 0.435 | 0.555 | 0.337 | 0.333 | – |
| [RewardBench 2](https://huggingface.co/datasets/allenai/reward-bench-2) | 1,200 | 79.2 | – | – | – | 66.9 | 60.0 | 56.0 | **81.5** | 72.9* | 74.9 | 75.0 | 63.2 | 48.6 | 79.3 | 64.3 | – | – |
| **Images** | | | | | | | | | | | | | | | | | | |
| [ScienceQA images](https://huggingface.co/datasets/derek-thomas/ScienceQA) | 500 | – | – | **82.8** | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| [VQA-RAD](https://huggingface.co/datasets/flaviagiammarino/vqa-rad) | 251 | – | – | **78.1** | – | – | – | – | – | – | – | – | – | – | – | – | – | – |

– not run, or not supported by that API (option limits, question types, no image input). \* under 99.5% of cases answered, from refusals or errors. † Liquid D1 through OpenRouter, the same hosted service.

Explore every cell, with intervals and examples, on the [website](https://leanmcp.github.io/jevbench/). Where each model runs: [Models](#models).
<!-- results:end -->

### What the paper adds

Beyond accuracy, the paper reports, for Jev, D1, djev and Laya:

- **Threshold effects.** Jev separates prompt injections almost perfectly
  (AUROC 0.978) but scores 73.3% at the default 0.5 cut-off, because its
  probabilities sit low.
- **Option-order sensitivity.** Reordering the options of a multiple-choice
  question flips correctness on 2.6–5.4% of items for Jev and 12.0–33.6% for
  djev and Laya.
- **Calibration and zero mass on the gold option**, and **image-grounded
  decisions** for djev (82.8% on ScienceQA rows with images).

How models are added and what each costs: [the decision-models runbook](jev_bench/05_DECISION_MODELS.md).

## Ranking and scoring

Beyond classification, JevBench tests decision models as **rerankers** and as
**judges**; their results are in the table above.

| Benchmark | What it tests | How the model is asked |
|---|---|---|
| SciFact, NFCorpus | Reranking a fixed BM25 top-20 of scientific and medical abstracts; nDCG@10 | Per document (one yes/no question per document, in one request) and all-at-once (one choice over the 20); graded relevance on NFCorpus |
| HelpSteer2 | Rating answer helpfulness 0–4 like a human annotator; Spearman correlation | One score question |
| RewardBench 2 | Picking the one correct response of four; accuracy per subset | One choice, asked in two orders |

How each works and why: [the ranking and scoring runbook](jev_bench/06_RANK_SCORE.md).

## What a typed decision model is

A typed decision model does not write text. It reads a state and a set of typed
questions and returns a probability for every allowed answer:

- **noul**: a yes/no question, answered with the probability of yes
- **choice**: one option from a fixed set, answered with a distribution over the set
- **score**: a level on an ordered rubric, answered with a distribution and its expected level

JevBench sends every model the same request and scores the probabilities it
returns against labels the model never sees.

## The dataset

Rows from twelve public datasets, turned into 12 text slices and 2 image slices of
typed-decision cases. Every
multiple-choice question also has a reordered twin, which is how option-order
sensitivity is measured.

| Domain | Slices | Source licence |
|---|---|---|
| Medicine | MedMCQA, MedQA-USMLE, PubMedQA | Apache 2.0, CC BY 4.0, MIT |
| Examinations | MMLU-Pro, ScienceQA | MIT, CC BY-SA 4.0 |
| Banking intent | BANKING77 | MIT |
| Sentiment | SST-5 | not stated on its card; text withheld from the release |
| Agent safety | Aegis 2.0 (prompts and responses), ATBench, prompt injections, jailbreak classification | CC BY 4.0, Apache 2.0, Apache 2.0, Apache 2.0 |
| Images | VQA-RAD, ScienceQA with images | CC0 1.0, CC BY-SA 4.0 |

The cases and every model's predictions are on
[Hugging Face](https://huggingface.co/datasets/Leanmcp/jevbench). Predictions
hold the decision and the probabilities, never the source text. Each source is
read at a pinned revision listed in [`jev_bench/sources.json`](jev_bench/sources.json).

## Quick start

```bash
cd jev_bench
uv sync
uv run workspace/download.py               # every source at its pinned revision
uv run workspace/build_cases.py --permute  # text slices plus reordered twins
uv run workspace/verify_cases.py           # leakage and consistency checks
uv run workspace/run_eval.py --dry-run     # build every request, send nothing
```

To see which model has run on which dataset, and run only the missing cells:

```bash
uv run workspace/matrix.py          # arrow keys to move, space to select, enter to run
```

Models live in [`jev_bench/models.json`](jev_bench/models.json); adding one is one
entry. Or call a single endpoint directly:

| Endpoint | Key | Runbook |
|---|---|---|
| `--endpoint jev` | `TYPESAFE_API_KEY` | [02_RUNNING.md](jev_bench/02_RUNNING.md) |
| `--endpoint liquid` | `LIQUID_API_KEY` | [03_LIQUID_D1.md](jev_bench/03_LIQUID_D1.md) |
| `--endpoint openrouter --model <id>` | `OPENROUTER_API_KEY` | [05_DECISION_MODELS.md](jev_bench/05_DECISION_MODELS.md) |
| `--endpoint d1local` | none, runs on your machine | [05_DECISION_MODELS.md](jev_bench/05_DECISION_MODELS.md) |
| `--endpoint djev` | none, self-hosted GPU | [djev-v1/](djev-v1/) |

MCPMark and MCP-Bench tool-routing slices are covered in
[04_MCP_BENCHMARKS.md](jev_bench/04_MCP_BENCHMARKS.md).

## Repository layout

| Path | Contents |
|---|---|
| `jev_bench/` | The harness: source manifest, download, adapters, case building, evaluation, scoring |
| `paper/latex/` | The paper source |
| `djev-v1/` | Serving djev on a single A100 |
| `Laya_Architecture/` | Laya's architecture and a local trial script |
| `jev_gateway/` | Example: a safety gate that routes a conversation through a Jev decision |
| `quick_benchmark/` | A small smoke test |
| `model_workspace/reference/` | Published configuration files for DiffusionGemma and Laya |

## Contributing

New datasets and new models are welcome. [CONTRIBUTING.md](CONTRIBUTING.md)
covers setup and the rules every change follows. Report security issues
privately as described in [SECURITY.md](SECURITY.md).

## Licence

The code is released under the [MIT Licence](LICENSE). Cases derived from public
datasets keep their original licences, listed in the dataset table above and
recorded per row in the released cases. Model weights keep their own licences.

## Citation

```bibtex
@misc{pai2026jevbench,
  title        = {{JevBench}: An Open Evaluation Framework for Typed Decision Models},
  author       = {Pai, Dheeraj Mohandas and Xian, Lu},
  year         = {2026},
  howpublished = {Preprints.org},
  url          = {https://www.preprints.org/manuscript/202610.0181}
}
```

## Models

<!-- models:start -->
| Model | Runs on | Served through |
|---|---|---|
| Jev 1.13 | API | TypeSafe API |
| Liquid D1 | API | Liquid API and OpenRouter |
| djev-0.1 | Cloud GPU | GCP A100 |
| Laya 421M | Local | local server |
| Clef | API | OpenRouter |
| Clef-flash | API | OpenRouter |
| Clef-omni | API | OpenRouter |
| pplx-decider v1.1 | API | OpenRouter |
| GPT-6 Luna Decisions | API | OpenRouter |
| Microsoft Decision 1 | API | OpenRouter |
| Solar Decide | API | OpenRouter |
| Solar Decide Flash | API | OpenRouter |
| Drex v1.5 | API | OpenRouter |
| Mercury Decide | API | OpenRouter |
| TEv1 4B (exp.) | API | OpenRouter |
| Kev 4B | API | OpenRouter |
| Span-01 | API | OpenRouter |
<!-- models:end -->
