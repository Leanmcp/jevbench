# jev-bench results: or-upstage-solar-decide-flash-full

Scored 2026-10-11T19:43:51-0700. Model requested `or-upstage-solar-decide-flash`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.7360** | [0.698, 0.774] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7200** | [0.680, 0.760] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.5000** | [0.456, 0.544] | accuracy |
| banking77 | choice | 174 | 0.0% | no usable records | n/a | n/a |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.0920** | [1.020, 1.175] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9700** | [0.953, 0.985] | accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **0.7308** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4053** | [0.334, 0.476] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **0.9444** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.6340** | [0.598, 0.672] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.7220** | [0.686, 0.758] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.4720** | [0.435, 0.513] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 96.6% | **0.3044** | [0.270, 0.337] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3638** | [0.330, 0.401] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3297** | [0.295, 0.366] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.7931** | [0.716, 0.862] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.5240** | [0.480, 0.568] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.6325** | [0.601, 0.664] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.8560** | [0.829, 0.881] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.6372** | [0.587, 0.687] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.6605** | [0.617, 0.704] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.7212** | [0.655, 0.791] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| mcpbench_tool_selection | 26 | 13 | 73.1% | 0.6821 | 0.3343 | 0.7117 | 0 | 0.1493 | 26 |
| mcpmark_server_routing | 338 | 8 | 40.5% | 0.3245 | 0.7551 | 1.8109 | 0 | 0.1862 | 338 |
| mcpmark_tool_selection | 18 | 5 | 94.4% | 0.9492 | 0.1249 | 0.2765 | 0 | 0.1299 | 18 |
| medmcqa | 1000 | 4 | 63.4% | 0.6336 | 0.5094 | 0.9975 | 0 | 0.1238 | 1000 |
| medqa_usmle | 1000 | 4 | 72.2% | 0.7211 | 0.4029 | 0.7631 | 0 | 0.0990 | 1000 |
| mmlu_pro | 1000 | 10 | 47.2% | 0.4697 | 0.6823 | 1.6581 | 0 | 0.1570 | 1000 |
| pubmedqa | 500 | 3 | 52.4% | 0.4907 | 0.7000 | 1.2564 | 0 | 0.2575 | 500 |
| rewardbench2 | 1200 | 4 | 63.2% | 0.6309 | 0.4696 | 0.9072 | 0 | 0.0416 | 1200 |
| scienceqa_text | 1000 | 4 | 85.6% | 0.8657 | 0.1967 | 0.3144 | 0 | 0.0229 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 73.6% | 26.4% | 53.6% | 6.4% | 0.8451 | 0.1881 | 0.1068 | 50.0% |
| aegis2_response | 500 | 72.0% | 28.0% | 50.0% | 6.0% | 0.8647 | 0.2021 | 0.1325 | 50.0% |
| atbench500 | 500 | 50.0% | 50.0% | 86.4% | 86.4% | 0.6266 | 0.3056 | 0.2600 | 50.0% |
| jailbreak_classification | 400 | 97.0% | 3.0% | 95.7% | 2.3% | 0.9883 | 0.0350 | 0.0615 | 35.2% |
| prompt_injections | 116 | 79.3% | 20.7% | 68.3% | 8.9% | 0.9051 | 0.1303 | 0.0567 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 27.6% | 73.6% | 1.092 | 0.2001 | 0.354 |
| nfcorpus_rank_graded | 4924 | 3 | 52.8% | 89.5% | 0.597 | 0.2018 | 0.437 |
| sst5 | 500 | 5 | 47.6% | 86.4% | 0.721 | 0.1475 | 0.802 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 288 | 0.3044 | 0.5640 | 0.1345 | 0.3295 | 0.4673 | 18.8% |
| nfcorpus_rank_graded | 298 | 0.3638 | 0.6116 | 0.1706 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3297 | 0.5375 | 0.1634 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.6372 | 0.6227 | 0.7330 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.6605 | 0.6212 | 0.8016 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 54.2% |
| rewardbench2 | Focus | 240 | 85.8% |
| rewardbench2 | Math | 240 | 53.3% |
| rewardbench2 | Precise IF | 240 | 30.4% |
| rewardbench2 | Safety | 240 | 92.5% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| mcpbench_tool_selection | 4 | 69.2% | 76.9% | 50.0% | 25.0% |
| mcpmark_server_routing | 169 | 40.2% | 40.8% | 32.5% | 16.0% |
| mcpmark_tool_selection | 3 | 88.9% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 63.6% | 63.2% | 52.8% | 21.2% |
| medqa_usmle | 500 | 71.2% | 73.2% | 65.4% | 13.6% |
| mmlu_pro | 500 | 47.4% | 47.0% | 37.4% | 19.6% |
| rewardbench2 | 594 | 61.8% | 64.7% | 47.3% | 31.8% |
| scienceqa_text | 500 | 86.4% | 84.8% | 78.6% | 14.0% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 640 | 6175 | 6397 | 505 | 252,268 | 0 |
| aegis2_response | 585 | 728 | 1444 | 607 | 303,429 | 0 |
| atbench500 | 638 | 891 | 1134 | 2223 | 1,111,555 | 0 |
| helpsteer2_helpfulness | 661 | 5182 | 5759 | 934 | 467,105 | 0 |
| jailbreak_classification | 574 | 712 | 1415 | 713 | 285,150 | 0 |
| mcpbench_tool_selection | 564 | 640 | 640 | 915 | 23,778 | 0 |
| mcpmark_server_routing | 560 | 691 | 2157 | 470 | 159,016 | 0 |
| mcpmark_tool_selection | 574 | 2077 | 2077 | 647 | 11,642 | 0 |
| medmcqa | 559 | 744 | 1398 | 399 | 399,370 | 0 |
| medqa_usmle | 572 | 747 | 1651 | 554 | 553,650 | 0 |
| mmlu_pro | 569 | 716 | 1138 | 545 | 544,710 | 0 |
| nfcorpus_rank_choice | 1073 | 1516 | 2043 | 2503 | 720,835 | 0 |
| nfcorpus_rank_graded | 576 | 960 | 1457 | 570 | 2,807,330 | 0 |
| nfcorpus_rank_noul | 2069 | 3121 | 3644 | 48457 | 14,440,038 | 0 |
| prompt_injections | 627 | 817 | 918 | 497 | 57,662 | 0 |
| pubmedqa | 570 | 694 | 1042 | 711 | 355,398 | 0 |
| rewardbench2 | 673 | 1086 | 1435 | 1957 | 2,348,908 | 0 |
| scienceqa_text | 556 | 649 | 983 | 402 | 402,396 | 0 |
| scifact_rank_choice | 1145 | 1631 | 1951 | 2897 | 869,148 | 0 |
| scifact_rank_noul | 2173 | 2894 | 3232 | 61557 | 18,467,080 | 0 |
| sst5 | 586 | 1008 | 1214 | 390 | 194,814 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** banking77: 174, nfcorpus_rank_choice: 10. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-upstage-solar-decide-flash-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

