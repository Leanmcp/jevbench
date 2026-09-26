# jev-bench results: djev-full

Scored 2026-09-26T20:43:42+0800. Model requested `djev-0.1`, endpoint `http://127.0.0.1:18000/v1/request`, manifest pinned 2026-09-26. One typed question per request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8100** | [0.774, 0.842] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.6920** | [0.652, 0.730] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7580** | [0.718, 0.796] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.7140** | [0.678, 0.750] | accuracy |
| jailbreak_classification | noul | 400 | 100.0% | **0.9650** | [0.945, 0.983] | accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.5380** | [0.501, 0.574] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.7120** | [0.675, 0.748] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.4230** | [0.385, 0.459] | accuracy |
| prompt_injections | noul | 116 | 100.0% | **0.6466** | [0.560, 0.733] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6220** | [0.582, 0.664] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.8470** | [0.820, 0.873] | accuracy |
| sst5 | score | 500 | 100.0% | **0.5440** | [0.501, 0.588] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 71.4% | 0.6971 | 0.4644 | 1.7356 | 0 | 0.1961 | 1000 |
| medmcqa | 1000 | 4 | 53.8% | 0.5373 | 0.6506 | 1.4068 | 0 | 0.2299 | 1000 |
| medqa_usmle | 1000 | 4 | 71.2% | 0.7114 | 0.4369 | 1.0359 | 0 | 0.1653 | 1000 |
| mmlu_pro | 1000 | 10 | 42.3% | 0.4214 | 0.7922 | 2.2724 | 0 | 0.2537 | 1000 |
| pubmedqa | 500 | 3 | 62.2% | 0.5842 | 0.6458 | 1.5702 | 0 | 0.2794 | 500 |
| scienceqa_text | 1000 | 4 | 84.7% | 0.8466 | 0.2096 | 0.3518 | 0 | 0.0601 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 81.0% | 19.0% | 63.6% | 1.6% | 0.9136 | 0.1778 | 0.1682 | 50.0% |
| aegis2_response | 500 | 69.2% | 30.8% | 41.6% | 3.2% | 0.8794 | 0.2722 | 0.2667 | 50.0% |
| atbench500 | 500 | 75.8% | 24.2% | 55.6% | 4.0% | 0.8548 | 0.2078 | 0.1898 | 50.0% |
| jailbreak_classification | 400 | 96.5% | 3.5% | 90.1% | 0.0% | 0.9922 | 0.0329 | 0.0343 | 35.2% |
| prompt_injections | 116 | 64.7% | 35.3% | 31.7% | 0.0% | 0.8801 | 0.3290 | 0.3328 | 51.7% |

`acc if flipped` exists because two upstream cards never state which integer means unsafe. If that column is the higher one, the mapping in `common.POLARITY_ASSUMPTIONS` is wrong and neither number should be quoted until it is fixed. AUROC is threshold-free, so it is the fairer comparison between models with differently placed probabilities.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS |
|---|---|---|---|---|---|---|
| sst5 | 500 | 5 | 49.8% | 96.8% | 0.544 | 0.1115 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 72.0% | 70.8% | 65.4% | 12.0% |
| medmcqa | 500 | 52.2% | 55.4% | 40.6% | 26.4% |
| medqa_usmle | 500 | 71.4% | 71.0% | 64.0% | 14.4% |
| mmlu_pro | 500 | 41.6% | 43.0% | 32.0% | 20.6% |
| scienceqa_text | 500 | 83.8% | 85.6% | 77.0% | 15.4% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 847 | 1039 | 15444 | 231 | 115,381 | 0 |
| aegis2_response | 845 | 947 | 1010 | 336 | 168,205 | 0 |
| atbench500 | 1265 | 1943 | 2155 | 1988 | 993,831 | 0 |
| banking77 | 849 | 1074 | 1176 | 1207 | 1,207,286 | 0 |
| jailbreak_classification | 838 | 944 | 1051 | 441 | 176,561 | 0 |
| medmcqa | 743 | 891 | 985 | 172 | 171,512 | 0 |
| medqa_usmle | 847 | 1022 | 1123 | 333 | 332,860 | 0 |
| mmlu_pro | 843 | 998 | 1059 | 328 | 327,650 | 0 |
| prompt_injections | 897 | 1034 | 1067 | 221 | 25,666 | 0 |
| pubmedqa | 824 | 1014 | 1113 | 494 | 247,117 | 0 |
| scienceqa_text | 781 | 966 | 1035 | 174 | 173,702 | 0 |
| sst5 | 769 | 952 | 1037 | 154 | 77,029 | 0 |

Measured end to end from this client at concurrency 6, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## Comparison

| slice | metric | djev-full | jev-1.13.0-20260926T133639 | delta |
|---|---|---|---|---|
| aegis2 | accuracy | 0.8100 | 0.8280 | -0.0180 |
| aegis2_response | accuracy | 0.6920 | 0.8120 | -0.1200 |
| atbench500 | accuracy | 0.7580 | 0.9300 | -0.1720 |
| banking77 | accuracy | 0.7140 | 0.8130 | -0.0990 |
| jailbreak_classification | accuracy | 0.9650 | 0.9750 | -0.0100 |
| medmcqa | accuracy | 0.5380 | 0.7810 | -0.2430 |
| medqa_usmle | accuracy | 0.7120 | 0.8730 | -0.1610 |
| mmlu_pro | accuracy | 0.4230 | 0.8060 | -0.3830 |
| prompt_injections | accuracy | 0.6466 | 0.7328 | -0.0862 |
| pubmedqa | accuracy | 0.6220 | 0.7060 | -0.0840 |
| scienceqa_text | accuracy | 0.8470 | 0.9570 | -0.1100 |
| sst5 | mae_expected_level | 0.5440 | 0.5071 | +0.0369 |

These are unpaired point differences. A paired bootstrap on shared case ids is the right test before claiming one model beats the other.

## What these numbers do not establish

- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/djev-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

