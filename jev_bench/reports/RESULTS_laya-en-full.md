# jev-bench results: laya-en-full

Scored 2026-09-26T19:50:46+0800. Model requested `english`, endpoint `http://127.0.0.1:8000/v1/systemone`, manifest pinned 2026-09-26. One typed question per request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.5420** | [0.496, 0.588] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.5280** | [0.486, 0.572] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.6540** | [0.610, 0.694] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.3630** | [0.326, 0.401] | accuracy |
| jailbreak_classification | noul | 400 | 100.0% | **0.9300** | [0.902, 0.955] | accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.2690** | [0.236, 0.304] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.2610** | [0.229, 0.294] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.1250** | [0.102, 0.151] | accuracy |
| prompt_injections | noul | 116 | 100.0% | **0.8103** | [0.733, 0.879] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.3280** | [0.288, 0.372] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.5340** | [0.500, 0.569] | accuracy |
| sst5 | score | 500 | 100.0% | **0.8493** | [0.796, 0.905] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 36.3% | 0.3235 | 1.1602 | 2.5173 | 349 | 0.5571 | 1000 |
| medmcqa | 1000 | 4 | 26.9% | 0.2562 | 0.8375 | 1.5628 | 0 | 0.2070 | 1000 |
| medqa_usmle | 1000 | 4 | 26.1% | 0.2587 | 0.8457 | 1.5611 | 0 | 0.2224 | 1000 |
| mmlu_pro | 1000 | 10 | 12.5% | 0.1167 | 0.9911 | 2.5744 | 0 | 0.2354 | 1000 |
| pubmedqa | 500 | 3 | 32.8% | 0.2571 | 0.9904 | 1.8372 | 0 | 0.4336 | 500 |
| scienceqa_text | 1000 | 4 | 53.4% | 0.5087 | 0.5537 | 0.8431 | 0 | 0.1061 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 54.2% | 45.8% | 23.2% | 14.8% | 0.6037 | 0.3071 | 0.2283 | 50.0% |
| aegis2_response | 500 | 52.8% | 47.2% | 14.8% | 9.2% | 0.5600 | 0.2960 | 0.2042 | 50.0% |
| atbench500 | 500 | 65.4% | 34.6% | 49.2% | 18.4% | 0.7356 | 0.2295 | 0.1000 | 50.0% |
| jailbreak_classification | 400 | 93.0% | 7.0% | 100.0% | 10.8% | 0.9977 | 0.0505 | 0.0123 | 35.2% |
| prompt_injections | 116 | 81.0% | 19.0% | 68.3% | 5.4% | 0.9223 | 0.1386 | 0.0562 | 51.7% |

`acc if flipped` exists because two upstream cards never state which integer means unsafe. If that column is the higher one, the mapping in `common.POLARITY_ASSUMPTIONS` is wrong and neither number should be quoted until it is fixed. AUROC is threshold-free, so it is the fairer comparison between models with differently placed probabilities.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS |
|---|---|---|---|---|---|---|
| sst5 | 500 | 5 | 33.8% | 83.8% | 0.849 | 0.1508 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 38.8% | 33.8% | 28.2% | 16.2% |
| medmcqa | 500 | 27.6% | 26.2% | 16.0% | 21.8% |
| medqa_usmle | 500 | 27.2% | 25.0% | 15.8% | 20.6% |
| mmlu_pro | 500 | 12.8% | 12.2% | 6.0% | 13.0% |
| scienceqa_text | 500 | 53.6% | 53.2% | 36.6% | 33.6% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 248 | 590 | 645 | 142 | 71,249 | 0 |
| aegis2_response | 482 | 577 | 707 | 256 | 127,948 | 0 |
| atbench500 | 907 | 958 | 1050 | 512 | 255,899 | 0 |
| banking77 | 637 | 825 | 1134 | 340 | 340,204 | 0 |
| jailbreak_classification | 1956 | 2856 | 3216 | 281 | 112,481 | 0 |
| medmcqa | 888 | 1068 | 1204 | 79 | 79,390 | 0 |
| medqa_usmle | 1780 | 2356 | 2810 | 236 | 235,964 | 0 |
| mmlu_pro | 1474 | 2669 | 3074 | 191 | 191,328 | 0 |
| prompt_injections | 1240 | 1513 | 1572 | 145 | 16,822 | 0 |
| pubmedqa | 2691 | 3021 | 3522 | 380 | 190,045 | 0 |
| scienceqa_text | 870 | 1052 | 1222 | 87 | 86,706 | 0 |
| sst5 | 836 | 894 | 922 | 74 | 37,070 | 0 |

Measured end to end from this client at concurrency 8, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/laya-en-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

