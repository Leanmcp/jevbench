# jev-bench results: clm-v0.1-8B-full

Scored 2026-09-27T13:14:43+0800. Model requested `clm-v0.1-8B`, endpoint `http://127.0.0.1:18700/v1/systemone`, manifest pinned 2026-09-26. One typed question per request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.5020** | [0.458, 0.550] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.5000** | [0.456, 0.546] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.3580** | [0.316, 0.400] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.0260** | [0.014, 0.040] | accuracy |
| jailbreak_classification | noul | 400 | 100.0% | **0.3525** | [0.307, 0.400] | accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.2240** | [0.190, 0.261] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.2650** | [0.228, 0.302] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.1430** | [0.112, 0.176] | accuracy |
| prompt_injections | noul | 116 | 100.0% | **0.5172** | [0.422, 0.612] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.2340** | [0.198, 0.274] | accuracy |
| scienceqa_image | choice | 500 | 100.0% | **0.4080** | [0.366, 0.450] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.4960** | [0.454, 0.539] | accuracy |
| sst5 | score | 500 | 100.0% | **0.9758** | [0.916, 1.033] | mae_expected_level |
| vqa_rad | noul | 251 | 100.0% | **0.5179** | [0.454, 0.578] | accuracy |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 2.6% | 0.0042 | 1.0418 | 5.7130 | 0 | 0.1718 | 1000 |
| medmcqa | 1000 | 4 | 22.4% | 0.2235 | 1.0714 | 2.5653 | 0 | 0.4421 | 1000 |
| medqa_usmle | 1000 | 4 | 26.5% | 0.2649 | 1.0495 | 2.4525 | 0 | 0.4312 | 1000 |
| mmlu_pro | 1000 | 10 | 14.3% | 0.1421 | 1.0568 | 3.2474 | 0 | 0.3032 | 1000 |
| pubmedqa | 500 | 3 | 23.4% | 0.1729 | 1.0157 | 1.7138 | 0 | 0.4551 | 500 |
| scienceqa_image | 500 | 4 | 40.8% | 0.3740 | 0.8359 | 1.7201 | 0 | 0.2926 | 500 |
| scienceqa_text | 1000 | 4 | 49.6% | 0.4707 | 0.6866 | 1.2432 | 0 | 0.2736 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 50.2% | 49.8% | 99.6% | 99.2% | 0.8267 | 0.3131 | 0.3219 | 50.0% |
| aegis2_response | 500 | 50.0% | 50.0% | 100.0% | 100.0% | 0.7057 | 0.4426 | 0.4479 | 50.0% |
| atbench500 | 500 | 35.8% | 64.2% | 64.4% | 92.8% | 0.4754 | 0.4145 | 0.4354 | 50.0% |
| jailbreak_classification | 400 | 35.2% | 64.8% | 100.0% | 100.0% | 0.8256 | 0.4954 | 0.5440 | 35.2% |
| prompt_injections | 116 | 51.7% | 48.3% | 100.0% | 100.0% | 0.8101 | 0.3685 | 0.3901 | 51.7% |
| vqa_rad | 251 | 51.8% | 48.2% | 10.2% | 11.3% | 0.5024 | 0.3418 | 0.2833 | 47.0% |

`acc if flipped` exists because two upstream cards never state which integer means unsafe. If that column is the higher one, the mapping in `common.POLARITY_ASSUMPTIONS` is wrong and neither number should be quoted until it is fixed. AUROC is threshold-free, so it is the fairer comparison between models with differently placed probabilities.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS |
|---|---|---|---|---|---|---|
| sst5 | 500 | 5 | 29.6% | 77.4% | 0.976 | 0.2045 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 2.6% | 2.6% | 2.6% | 0.0% |
| medmcqa | 500 | 22.6% | 22.2% | 22.0% | 0.8% |
| medqa_usmle | 500 | 26.4% | 26.6% | 26.4% | 0.2% |
| mmlu_pro | 500 | 14.4% | 14.2% | 14.2% | 0.2% |
| scienceqa_text | 500 | 49.6% | 49.6% | 49.4% | 0.4% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 907 | 1050 | 1133 | 121 | 59,314 | 0 |
| aegis2_response | 935 | 1071 | 1126 | 222 | 111,024 | 0 |
| atbench500 | 929 | 1126 | 1226 | 1519 | 759,592 | 0 |
| banking77 | 585 | 863 | 2904 | 33 | 26,582 | 0 |
| jailbreak_classification | 706 | 993 | 1179 | 320 | 127,753 | 0 |
| medmcqa | 651 | 754 | 811 | 57 | 56,065 | 0 |
| medqa_usmle | 706 | 846 | 870 | 215 | 208,547 | 0 |
| mmlu_pro | 695 | 818 | 866 | 172 | 169,926 | 0 |
| prompt_injections | 657 | 851 | 872 | 104 | 9,999 | 0 |
| pubmedqa | 720 | 898 | 964 | 368 | 183,802 | 0 |
| scienceqa_image | 635 | 749 | 793 | 81 | 29,077 | 0 |
| scienceqa_text | 652 | 760 | 828 | 61 | 58,466 | 0 |
| sst5 | 587 | 736 | 780 | 37 | 18,313 | 0 |
| vqa_rad | 605 | 763 | 785 | 27 | 6,307 | 0 |

Measured end to end from this client at concurrency 24, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_image (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/clm-v0.1-8B-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

