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

Accuracy (%) on 8,014 cases answered by all four systems. Bold marks the best
model on each slice.

| Slice | n | Liquid D1 | Jev 1.13 | djev-0.1 | Laya 421M |
|---|---:|---:|---:|---:|---:|
| ScienceQA (text) | 1000 | **95.8** | 95.7 | 84.7 | 53.4 |
| Jailbreak classification | 400 | 96.5 | **97.5** | 96.5 | 93.0 |
| MedQA-USMLE | 1000 | 86.6 | **87.3** | 71.2 | 26.1 |
| Aegis 2.0 prompts | 500 | **86.6** | 82.8 | 81.0 | 54.2 |
| BANKING77 (77 intents) | 1000 | **85.7** | 81.3 | 71.4 | 36.3 |
| ATBench agent safety | 500 | 78.6 | **93.0** | 75.8 | 65.4 |
| Aegis 2.0 responses | 500 | 78.8 | **81.2** | 69.2 | 52.8 |
| MedMCQA | 1000 | 77.0 | **78.1** | 53.8 | 26.9 |
| Prompt injections | 116 | 71.6 | 73.3 | 64.7 | **81.0** |
| PubMedQA | 500 | 70.4 | **70.6** | 62.2 | 32.8 |
| MMLU-Pro | 998 | 66.4 | **80.6** | 42.2 | 12.5 |
| SST-5, MAE (lower is better) | 500 | 0.508 | **0.507** | 0.544 | 0.849 |

No single model leads everywhere. D1 is ahead on BANKING77 (+4.4 points over
Jev) and Aegis prompts (+3.8); Jev is ahead on ATBench (+14.4) and MMLU-Pro
(+14.1). These are point estimates; the paper gives bootstrap intervals and
paired comparisons for the original three systems.

Beyond accuracy, the paper reports:

- **Threshold effects.** Jev separates prompt injections almost perfectly
  (AUROC 0.978) but scores 73.3% at the default 0.5 cut-off, because its
  probabilities sit low.
- **Option-order sensitivity.** Reordering the options of a multiple-choice
  question flips correctness on 2.6–5.4% of items for Jev and 12.0–33.6% for
  djev and Laya.
- **Calibration and zero mass on the gold option**, and **image-grounded
  decisions** for djev (82.8% on ScienceQA rows with images).

### The systems

| System | Access | Model |
|---|---|---|
| Liquid D1 | Hosted API | Unpublished |
| Jev 1.13 | Hosted API | Unpublished |
| djev-0.1 | Open source | DiffusionGemma 26B-A4B, a text diffusion language model |
| Laya 421M | Open source | ModernBERT-large encoder with decision heads |

Thirteen more hosted decision models, including Cloudflare Clef and Perplexity
pplx-decider, plus Liquid's open d1-3B and d1-omni-600M, are wired in and
waiting on runs. See [the decision-models runbook](jev_bench/05_DECISION_MODELS.md).

## Ranking and scoring

Beyond classification, JevBench tests decision models as **rerankers** and as
**judges**. Results are pending.

| Benchmark | What it tests | How the model is asked |
|---|---|---|
| SciFact, NFCorpus | Reranking a fixed BM25 top-20 of scientific and medical abstracts; nDCG@10 | Jev-style (one noul per document in one request) and all-at-once (one choice over the 20); graded relevance on NFCorpus |
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
