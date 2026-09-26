# jev-bench results: jev-1.13.0-20260926T133408

Scored 2026-09-26T13:35:34+0800. Model requested `jev-1.13.0`, endpoint `https://api.typesafe.ai/v1/systemone`, manifest pinned 2026-09-26. One typed question per request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| prompt_injections | noul | 20 | 100.0% | **0.8500** | [0.700, 1.000] | accuracy |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| prompt_injections | 20 | 85.0% | 15.0% | 62.5% | 0.0% | 0.9427 | 0.1272 | 0.1320 | 40.0% |

`acc if flipped` exists because two upstream cards never state which integer means unsafe. If that column is the higher one, the mapping in `common.POLARITY_ASSUMPTIONS` is wrong and neither number should be quoted until it is fixed. AUROC is threshold-free, so it is the fairer comparison between models with differently placed probabilities.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| prompt_injections | 1275 | 21832 | 21832 | 406 | 8,117 | 0 |

Measured end to end from this client at concurrency 2, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/jev-1.13.0-20260926T133408/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

