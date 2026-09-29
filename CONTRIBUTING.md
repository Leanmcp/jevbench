# Contributing to JevBench

Thank you for helping improve JevBench. This guide covers setup, the two most
common contributions (a new dataset and a new model), and the rules every change
has to follow.

## Setup

The harness lives in `jev_bench/` and uses [uv](https://docs.astral.sh/uv/).

```bash
cd jev_bench
uv sync
uv run workspace/download.py --list   # show what will be downloaded
uv run workspace/download.py          # fetch every source at its pinned revision
uv run workspace/build_cases.py --permute
uv run workspace/verify_cases.py
```

Add dependencies with `uv add <package>`. Do not use `pip install`.

## Adding a dataset

1. Add an entry to `jev_bench/sources.json`: the Hugging Face repository, the
   exact revision hash, the files to read, the licence, the fields the model may
   see (`model_visible`), the gold field, and every field that must stay hidden
   (`hidden`).
2. Write an adapter in `jev_bench/workspace/common.py` and register it in
   `ADAPTERS`. The adapter must build the state from the `model_visible` fields
   only.
3. Rebuild the cases and run `verify_cases.py`. It must report no hidden field
   in any state.
4. Add the slice's instructions and criteria to the prompts appendix of the
   paper, so the wording stays documented.

## Adding a model

`run_eval.py --endpoint` accepts `jev`, `djev`, or a full URL. A new model can
be evaluated without code changes if it serves the same typed-decision request
format. Always do a dry run first, then a small trial:

```bash
uv run workspace/run_eval.py --dry-run
uv run workspace/run_eval.py --endpoint <url> --model <name> --only prompt_injections --limit 20
```

## Rules for every change

- **Pin everything.** Every dataset is read at a fixed revision. Never write a
  dependency or dataset version from memory; look it up.
- **No leakage.** Gold labels, rationales and annotations never enter a
  request.
- **No source text in predictions.** Predictions record decisions and
  probabilities only.
- **Respect licences.** Do not add a source whose licence forbids
  redistribution unless its text is withheld from the release.
- **Report numbers you measured.** Any number in a pull request or in the paper
  must come from a run in `data/runs/`.

## Pull requests

Keep each pull request to one change, describe what you ran to check it, and
include the command output. For security issues, follow `SECURITY.md` instead of
opening a pull request.

## Licence

By contributing, you agree that your contributions are licensed under the MIT
Licence in `LICENSE`.
