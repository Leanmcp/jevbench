# jev-bench step 3: build, verify, run, score, report

Written 26 September 2026. Five scripts in `workspace/`, one base module and one per stage.

| File | Does | Network |
|---|---|---|
| [common.py](workspace/common.py) | Everything shared: readers, sampling, the 12 per-source adapters, the HTTP client, response parsing, printing | none at import |
| [build_cases.py](workspace/build_cases.py) | Rows to typed-decision cases in `data/cases/` | no |
| [verify_cases.py](workspace/verify_cases.py) | Leakage, gold reachability, request limits, context budget | no |
| [run_eval.py](workspace/run_eval.py) | Sends cases, writes `data/runs/<run_id>/predictions.jsonl` | yes |
| [score_runs.py](workspace/score_runs.py) | Metrics to `scores.json` | no |
| [report.py](workspace/report.py) | Final tables to `reports/RESULTS_<run_id>.md` | no |

## The key

`TYPESAFE_API_KEY` is read from the environment by name. It is never printed, never written to a file, never put in a URL or a command line, and if it ever appeared in an API error body it is scrubbed before that error is stored. `key_status()` returns presence and length only, which is what `verify_cases.py` prints.

## Run order

```bash
cd /Users/ddod/LEANMCP/JEV_RELATED/jev_bench

# 1. build cases. --permute adds an option-order twin for every MCQ case.
uv run workspace/build_cases.py --permute

# 2. verify before spending anything. Non-zero exit means do not proceed.
uv run workspace/verify_cases.py

# 3. look at one real request per slice
cat data/cases/previews/medmcqa.json

# 4. build every request body and send none
uv run workspace/run_eval.py --dry-run

# 5. a cheap real trial: 20 cases on the smallest slice
time uv run workspace/run_eval.py --only prompt_injections --limit 20

# 6. score and report that trial before committing to the full run
uv run workspace/score_runs.py --latest
uv run workspace/report.py --latest
```

Only after the trial reads correctly:

```bash
time uv run workspace/run_eval.py --concurrency 4
uv run workspace/score_runs.py --latest
uv run workspace/report.py --latest
```

A run is resumable. Re-running with the same `--run-id` skips case ids already recorded without an error, so an interrupted run continues rather than restarting. It also stops itself after 15 consecutive failures instead of burning the rest of the budget against a broken endpoint.

For a local djev on the A100 tunnel:

```bash
uv run workspace/run_eval.py --endpoint djev --model djev-0.1 --run-id djev-trial
```

## What gets built

12 text slices. `vqa_rad` is deliberately not built: it needs djev's image input, which the Jev API route here does not have. `scienceqa_text` is the image-null subset of ScienceQA, which is why it can run on Jev at all, and it doubles as the text-versus-image ablation once djev is up.

At the manifest's `target_n` and with `--permute`, expect roughly 5,900 cases, so roughly 5,900 requests at one question per request. Use `--n 25` for a full-pipeline rehearsal across every slice for about 300 requests.

## What verify_cases.py actually checks

The leakage check is the one that matters. It reloads the original rows and looks for each hidden field's text inside the state that would be sent. The gold option's text is excluded, since in a multiple-choice question the correct answer legitimately appears as one of the options; everything else is a hard failure. Rationale fields (`exp`, `cot_content`, `long_answer`, `solution`, `lecture`, `metamap_phrases`) are checked at a lower length threshold than ordinary fields because they are the expensive mistake.

It also flags cases above 512, 1,024 and 4,096 estimated tokens. Those estimates are 4 characters per token and are for triage only; `usage.input_tokens` from the API is the real count and is what the report uses.

## Decisions baked into the code, so they can be argued with

**One question per request.** Simple to score, and it makes latency per decision comparable across slices. It also gives up the thing Jev is fastest at, many questions against one state. That is a separate experiment, not a variable mixed into this one.

**Letter keys for MCQ, name keys for intents.** MedMCQA, MedQA, MMLU-Pro and ScienceQA present options as `a`/`b`/`c`/... with the option text as the description, so permuting which text sits under which letter moves the gold letter and measures position bias directly. BANKING77 uses the 77 intent names as keys, read from `label_text` in the data, and permutation there changes presentation order only.

**Truncation is recorded, not hidden.** States are capped at 12,000 characters. Every truncated case carries `truncated: true`, the count appears in the verify table and the scorer's output, and `report.py` writes it into the caveats section automatically so it cannot quietly fall out of the write-up.

**Polarity is reported both ways.** Neither ATBench nor `deepset/prompt-injections` states on its card which integer means unsafe. The assumption lives in `common.POLARITY_ASSUMPTIONS`, the scorer prints `accuracy_if_polarity_flipped` beside the real number, and it warns loudly if the flipped one is higher.

**`best_threshold_accuracy` is labelled optimistic** because it is chosen on the same data it scores. It is there to show the headroom a calibrated threshold would buy, not as a result.

**Predictions carry no state text.** `predictions.jsonl` holds the decision, the full probability vector, latency and token usage, keyed by `case_id`. That keeps it publishable even for SST-5, whose upstream license is unspecified, and it is the half of a benchmark release that people usually throw away.

## Metric conventions

Stated here because the numbers are meaningless without them. Brier is `mean_i sum_k (p_ik - y_ik)^2`, the sum convention. NLL is `-log p(gold)` with exact zeros counted in their own column rather than clipped out of sight; a clipped variant at 1e-12 sits beside it, labelled. ECE uses 10 equal-width bins on the top probability. Ordinal slices get MAE on the expected level plus the ranked probability score, with levels treated as equally spaced, which SST-5 does not actually guarantee. Confidence intervals are percentile bootstrap, 2,000 resamples, resampling whole `family_id` groups so a case and its reordered twin move together.

## Next after the first real run

1. Compare a djev run against the Jev run with `report.py --latest --compare <jev_run_id>`. Point differences only; a paired bootstrap on shared case ids is the honest test.
2. Add `vqa_rad` and the image-bearing ScienceQA rows once djev is serving, which is the only part of this that tests something no published Jev comparison covers.
3. Build the authorization cases from [the paper plan](../reports/Benchmark_and_paper_plan.md) section 3. Tiers 1 to 6 are context; that is the contribution.
4. Publish as two configs, `cases` and `predictions`, with per-source license fields and the `exposure` column intact.
