# jev-bench results: or-togethercomputer-tev1-4b-experimental-full

Scored 2026-10-11T20:05:42-0700. Model requested `or-togethercomputer-tev1-4b-experimental`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.7680** | [0.730, 0.804] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.6780** | [0.638, 0.718] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.5360** | [0.494, 0.582] | accuracy |
| banking77 | choice | 114 | 0.0% | no usable records | n/a | n/a |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.1578** | [1.078, 1.243] | mae_expected_level |
| jailbreak_classification | noul | 400 | 99.8% | **0.9173** | [0.890, 0.942] | accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **0.8846** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4497** | [0.376, 0.524] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.6100** | [0.569, 0.649] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.6890** | [0.652, 0.728] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.4840** | [0.445, 0.521] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 95.6% | **0.3571** | [0.322, 0.394] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3535** | [0.320, 0.389] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3606** | [0.326, 0.396] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.5517** | [0.466, 0.647] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6680** | [0.626, 0.710] | accuracy |
| rewardbench2 | choice | 1200 | 99.8% | **0.6427** | [0.610, 0.679] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.8850** | [0.860, 0.909] | accuracy |
| scifact_rank_choice | rank | 300 | 99.7% | **0.7217** | [0.677, 0.764] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7330** | [0.690, 0.774] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5231** | [0.485, 0.563] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| mcpbench_tool_selection | 26 | 13 | 88.5% | 0.8615 | 0.0922 | 0.1663 | 0 | 0.0848 | 26 |
| mcpmark_server_routing | 338 | 8 | 45.0% | 0.4326 | 0.7068 | 1.7487 | 0 | 0.0869 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0366 | 0.0699 | 0 | 0.0545 | 18 |
| medmcqa | 1000 | 4 | 61.0% | 0.6091 | 0.5004 | 0.9452 | 0 | 0.0762 | 1000 |
| medqa_usmle | 1000 | 4 | 68.9% | 0.6869 | 0.4172 | 0.7707 | 0 | 0.0580 | 1000 |
| mmlu_pro | 1000 | 10 | 48.4% | 0.4842 | 0.6548 | 1.7084 | 0 | 0.1344 | 1000 |
| pubmedqa | 500 | 3 | 66.8% | 0.6234 | 0.4910 | 0.9010 | 0 | 0.1390 | 500 |
| rewardbench2 | 1198 | 4 | 64.3% | 0.6429 | 0.4866 | 0.9817 | 0 | 0.0877 | 1198 |
| scienceqa_text | 1000 | 4 | 88.5% | 0.9003 | 0.1589 | 0.2573 | 0 | 0.0121 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 76.8% | 23.2% | 55.6% | 2.0% | 0.9041 | 0.1674 | 0.0927 | 50.0% |
| aegis2_response | 500 | 67.8% | 32.2% | 39.2% | 3.6% | 0.8710 | 0.2259 | 0.1831 | 50.0% |
| atbench500 | 500 | 53.6% | 46.4% | 38.4% | 31.2% | 0.4688 | 0.3086 | 0.1822 | 50.0% |
| jailbreak_classification | 399 | 91.7% | 8.3% | 76.4% | 0.0% | 0.9853 | 0.0598 | 0.0322 | 35.1% |
| prompt_injections | 116 | 55.2% | 44.8% | 13.3% | 0.0% | 0.9890 | 0.2594 | 0.3269 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 25.0% | 69.8% | 1.158 | 0.2145 | 0.337 |
| nfcorpus_rank_graded | 4924 | 3 | 51.7% | 91.2% | 0.591 | 0.2028 | 0.417 |
| sst5 | 500 | 5 | 59.0% | 96.2% | 0.523 | 0.0813 | 0.870 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 285 | 0.3571 | 0.6072 | 0.1645 | 0.3316 | 0.4698 | 18.9% |
| nfcorpus_rank_graded | 298 | 0.3535 | 0.5955 | 0.1699 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3606 | 0.5933 | 0.1709 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 299 | 0.7217 | 0.7017 | 0.8128 | 0.6627 | 0.8328 | 82.9% |
| scifact_rank_noul | 300 | 0.7330 | 0.7180 | 0.8167 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 50.8% |
| rewardbench2 | Focus | 240 | 95.4% |
| rewardbench2 | Math | 238 | 64.7% |
| rewardbench2 | Precise IF | 240 | 35.8% |
| rewardbench2 | Safety | 240 | 74.6% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| mcpbench_tool_selection | 4 | 84.6% | 92.3% | 75.0% | 25.0% |
| mcpmark_server_routing | 169 | 45.0% | 45.0% | 39.6% | 10.7% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 61.0% | 61.0% | 53.2% | 15.6% |
| medqa_usmle | 500 | 68.8% | 69.0% | 62.0% | 13.8% |
| mmlu_pro | 500 | 50.2% | 46.6% | 37.8% | 21.2% |
| rewardbench2 | 593 | 65.1% | 63.4% | 55.1% | 18.7% |
| scienceqa_text | 500 | 89.0% | 88.0% | 84.0% | 9.0% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 596 | 4793 | 4797 | 211 | 105,616 | 0 |
| aegis2_response | 611 | 687 | 696 | 314 | 156,847 | 6 |
| atbench500 | 2054 | 2509 | 2527 | 1921 | 960,597 | 0 |
| helpsteer2_helpfulness | 1066 | 6399 | 6420 | 702 | 350,919 | 0 |
| jailbreak_classification | 506 | 12447 | 18734 | 423 | 168,591 | 37 |
| mcpbench_tool_selection | 473 | 1329 | 1354 | 761 | 19,796 | 0 |
| mcpmark_server_routing | 438 | 993 | 1381 | 260 | 87,832 | 0 |
| mcpmark_tool_selection | 433 | 1210 | 1210 | 424 | 7,638 | 0 |
| medmcqa | 466 | 561 | 1658 | 162 | 162,126 | 0 |
| medqa_usmle | 575 | 955 | 1837 | 327 | 326,708 | 0 |
| mmlu_pro | 606 | 725 | 2101 | 342 | 342,153 | 0 |
| nfcorpus_rank_choice | 2611 | 3178 | 3197 | 2491 | 709,863 | 0 |
| nfcorpus_rank_graded | 595 | 802 | 2137 | 333 | 1,638,409 | 0 |
| nfcorpus_rank_noul | 12161 | 21193 | 25641 | 45551 | 13,574,243 | 271 |
| prompt_injections | 1976 | 14911 | 15269 | 201 | 23,321 | 24 |
| pubmedqa | 596 | 1774 | 1854 | 486 | 242,938 | 0 |
| rewardbench2 | 1191 | 1996 | 2581 | 1841 | 2,205,986 | 0 |
| scienceqa_text | 611 | 1655 | 2932 | 154 | 154,266 | 0 |
| scifact_rank_choice | 1629 | 4429 | 4617 | 3048 | 911,332 | 0 |
| scifact_rank_noul | 16545 | 19777 | 20709 | 60446 | 18,133,700 | 22 |
| sst5 | 488 | 1096 | 1852 | 158 | 78,769 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** banking77: 114, jailbreak_classification: 1, nfcorpus_rank_choice: 13, rewardbench2: 2, scifact_rank_choice: 1. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-togethercomputer-tev1-4b-experimental-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

