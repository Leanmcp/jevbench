# JevBench

An open evaluation framework for **typed decision models**: models that do not
generate text but return a typed decision, such as a probability for a yes/no
question, a distribution over a set of choices, or an expected level on an ordered
rubric.

JevBench turns rows of existing public datasets into typed-decision requests,
sends byte-identical requests to every model under test, and scores the returned
probability vectors against answers the models never see. Every case and every
prediction is released, so each number in the paper can be recomputed.

- **Paper:** *JevBench: An Open Evaluation Framework for Typed Decision Models*,
  source in [`paper/latex/`](paper/latex/)
- **Data:** cases and 24,799 predictions at
  [huggingface.co/datasets/Leanmcp/jevbench](https://huggingface.co/datasets/Leanmcp/jevbench)
  (tag `v0.1`)

This project is independent of, and not to be confused with, Benchmark Heaven's
[JevBench leaderboard](https://github.com/fstandhartinger/jevbench), which ranks
Jev-class models on a composite score.

## What it measures

Three systems on 12 text slices from eleven public datasets (medicine,
examinations, banking intent, sentiment and agent safety), plus two image slices:

| System | Access | Model |
|---|---|---|
| Jev 1.13 | Closed, vendor API | Unpublished |
| djev-0.1 | Open source | DiffusionGemma 26B-A4B, a text diffusion language model |
| Laya 421M | Open source | ModernBERT-large encoder with decision heads |

Beyond accuracy, the framework measures calibration and threshold effects,
sensitivity to the order in which options are presented (each set-of-choices
question has a reordered twin), probability mass on the correct option, and
paired bootstrap comparisons over shared cases.

## Quick start

The harness lives in [`jev_bench/`](jev_bench/) and uses [uv](https://docs.astral.sh/uv/).

```bash
cd jev_bench
uv sync
uv run workspace/download.py               # every source at its pinned revision
uv run workspace/build_cases.py --permute  # text slices plus reordered twins
uv run workspace/verify_cases.py           # leakage and consistency checks
uv run workspace/run_eval.py --dry-run     # build every request, send nothing
```

Evaluating the hosted model needs `TYPESAFE_API_KEY` in your environment. The GPU
scripts for djev read their cloud settings from `jev_bench/.env`; copy
[`jev_bench/.env.example`](jev_bench/.env.example) to start.
[`jev_bench/02_RUNNING.md`](jev_bench/02_RUNNING.md) covers full runs and scoring.

## Repository layout

| Path | Contents |
|---|---|
| `jev_bench/` | The harness: pinned source manifest (`sources.json`), download, adapters, case building and verification, evaluation, scoring, release staging |
| `paper/latex/` | The paper; one file per section in `sections/`, one TikZ file per figure in `figures/` |
| `djev-v1/` | Runbook for serving djev on a single A100 |
| `Laya_Architecture/` | Notes on Laya's architecture and a local trial script |
| `jev_gateway/` | Example: a safety gate that routes a conversation through a Jev decision |
| `quick_benchmark/` | A small smoke test used before the main runs |
| `model_workspace/reference/` | Published configuration files for the DiffusionGemma and Laya models |

## Licence

The code is released under the [MIT Licence](LICENSE). The cases derived from
public datasets keep their original licences, recorded per source in
`jev_bench/sources.json` and per row in the released cases. See
[CONTRIBUTING.md](CONTRIBUTING.md) to contribute and [SECURITY.md](SECURITY.md) to
report a security issue.

## Citation

```bibtex
@misc{pai2026jevbench,
  title  = {{JevBench}: An Open Evaluation Framework for Typed Decision Models},
  author = {Pai, Dheeraj Mohandas and Xian, Lu},
  year   = {2026},
  url    = {https://github.com/Leanmcp/jevbench}
}
```
