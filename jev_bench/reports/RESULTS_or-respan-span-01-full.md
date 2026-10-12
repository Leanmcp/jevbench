# jev-bench results: or-respan-span-01-full

Scored 2026-10-11T20:13:05-0700. Model requested `or-respan-span-01`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8180** | [0.784, 0.852] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7480** | [0.708, 0.784] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.6280** | [0.588, 0.670] | accuracy |
| banking77 | choice | 131 | 0.0% | no usable records | n/a | n/a |
| helpsteer2_helpfulness | score | 114 | 0.0% | no usable records | n/a | n/a |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 81.8% | 18.2% | 75.2% | 11.6% | 0.8912 | 0.1382 | 0.0763 | 50.0% |
| aegis2_response | 500 | 74.8% | 25.2% | 60.8% | 11.2% | 0.8461 | 0.1866 | 0.1218 | 50.0% |
| atbench500 | 500 | 62.8% | 37.2% | 32.4% | 6.8% | 0.6757 | 0.2658 | 0.1703 | 50.0% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 3416 | 6642 | 8385 | 236 | 117,751 | 0 |
| aegis2_response | 4060 | 4283 | 5390 | 369 | 184,436 | 0 |
| atbench500 | 5184 | 5402 | 6225 | 1975 | 987,280 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **Truncated states.** atbench500: 34. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** banking77: 131, helpsteer2_helpfulness: 114. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-respan-span-01-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

