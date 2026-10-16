# jev-bench results: or-liquid-d1-full

Scored 2026-10-15T23:38:25-0700. Model requested `or-liquid-d1`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8480** | [0.816, 0.880] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.8220** | [0.788, 0.854] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7580** | [0.718, 0.794] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8840** | [0.857, 0.910] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.0050** | [0.934, 1.079] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9700** | [0.953, 0.985] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9196** | [0.848, 0.982] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4586** | [0.388, 0.533] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7630** | [0.730, 0.796] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8810** | [0.854, 0.907] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6950** | [0.658, 0.730] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 96.6% | **0.3790** | [0.343, 0.415] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3763** | [0.342, 0.414] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3831** | [0.347, 0.418] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.7414** | [0.655, 0.819] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.7060** | [0.664, 0.746] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.7358** | [0.706, 0.765] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9560** | [0.939, 0.971] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7486** | [0.703, 0.790] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7305** | [0.685, 0.773] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5330** | [0.500, 0.569] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 88.4% | 0.8801 | 0.1687 | 0.3879 | 0 | 0.0344 | 1000 |
| mcpbench_server_routing | 112 | 28 | 92.0% | 0.9022 | 0.1389 | 0.2879 | 0 | 0.0475 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0046 | 0.0262 | 0 | 0.0242 | 26 |
| mcpmark_server_routing | 338 | 8 | 45.9% | 0.3753 | 0.6891 | 1.5768 | 0 | 0.1421 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0000 | 0.0021 | 0 | 0.0021 | 18 |
| medmcqa | 1000 | 4 | 76.3% | 0.7630 | 0.3379 | 0.6563 | 0 | 0.0628 | 1000 |
| medqa_usmle | 1000 | 4 | 88.1% | 0.8804 | 0.1830 | 0.3399 | 0 | 0.0359 | 1000 |
| mmlu_pro | 1000 | 10 | 69.5% | 0.6934 | 0.4256 | 0.9686 | 0 | 0.0667 | 1000 |
| pubmedqa | 500 | 3 | 70.6% | 0.5591 | 0.4418 | 0.9455 | 0 | 0.1610 | 500 |
| rewardbench2 | 1200 | 4 | 73.6% | 0.7347 | 0.3553 | 0.6706 | 0 | 0.0266 | 1200 |
| scienceqa_text | 1000 | 4 | 95.6% | 0.9640 | 0.0616 | 0.0963 | 0 | 0.0103 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 84.8% | 15.2% | 84.4% | 14.8% | 0.9307 | 0.1095 | 0.0510 | 50.0% |
| aegis2_response | 500 | 82.2% | 17.8% | 78.0% | 13.6% | 0.8971 | 0.1335 | 0.0415 | 50.0% |
| atbench500 | 500 | 75.8% | 24.2% | 56.0% | 4.4% | 0.9239 | 0.1522 | 0.0681 | 50.0% |
| jailbreak_classification | 400 | 97.0% | 3.0% | 91.5% | 0.0% | 0.9940 | 0.0278 | 0.0248 | 35.2% |
| prompt_injections | 116 | 74.1% | 25.9% | 50.0% | 0.0% | 0.9256 | 0.2278 | 0.2196 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 29.2% | 76.4% | 1.005 | 0.1765 | 0.547 |
| nfcorpus_rank_graded | 4924 | 3 | 64.8% | 97.2% | 0.433 | 0.1300 | 0.492 |
| sst5 | 500 | 5 | 54.0% | 98.4% | 0.533 | 0.0826 | 0.880 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 288 | 0.3790 | 0.6293 | 0.1688 | 0.3295 | 0.4673 | 18.8% |
| nfcorpus_rank_graded | 298 | 0.3763 | 0.6344 | 0.1729 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3831 | 0.6446 | 0.1758 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7486 | 0.7335 | 0.8234 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7305 | 0.7104 | 0.8184 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 73.8% |
| rewardbench2 | Focus | 240 | 90.4% |
| rewardbench2 | Math | 240 | 74.2% |
| rewardbench2 | Precise IF | 240 | 43.8% |
| rewardbench2 | Safety | 240 | 85.8% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 88.0% | 88.8% | 85.2% | 6.4% |
| mcpbench_server_routing | 56 | 91.1% | 92.9% | 91.1% | 1.8% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 44.4% | 47.3% | 39.6% | 12.4% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 76.8% | 75.8% | 70.4% | 11.8% |
| medqa_usmle | 500 | 87.8% | 88.4% | 85.4% | 5.4% |
| mmlu_pro | 500 | 69.8% | 69.2% | 62.4% | 14.2% |
| rewardbench2 | 594 | 72.8% | 74.3% | 64.8% | 17.5% |
| scienceqa_text | 500 | 96.0% | 95.2% | 93.6% | 4.0% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 460 | 4570 | 5481 | 165 | 82,588 | 0 |
| aegis2_response | 411 | 962 | 1567 | 270 | 135,182 | 0 |
| atbench500 | 722 | 1247 | 3106 | 1899 | 949,500 | 0 |
| banking77 | 458 | 820 | 2613 | 481 | 481,410 | 0 |
| helpsteer2_helpfulness | 492 | 5192 | 5639 | 641 | 320,337 | 0 |
| jailbreak_classification | 391 | 630 | 2360 | 382 | 152,929 | 0 |
| mcpbench_server_routing | 384 | 728 | 892 | 509 | 57,038 | 0 |
| mcpbench_tool_selection | 378 | 536 | 687 | 553 | 14,368 | 0 |
| mcpmark_server_routing | 396 | 850 | 1227 | 154 | 52,136 | 0 |
| mcpmark_tool_selection | 471 | 641 | 641 | 336 | 6,044 | 0 |
| medmcqa | 375 | 626 | 1462 | 96 | 95,623 | 1 |
| medqa_usmle | 403 | 876 | 1640 | 254 | 254,206 | 0 |
| mmlu_pro | 416 | 931 | 1174 | 218 | 217,800 | 0 |
| nfcorpus_rank_choice | 690 | 2447 | 4041 | 2243 | 645,964 | 0 |
| nfcorpus_rank_graded | 411 | 878 | 1934 | 286 | 1,409,049 | 1 |
| nfcorpus_rank_noul | 3671 | 6858 | 7622 | 47734 | 14,224,776 | 0 |
| prompt_injections | 995 | 2864 | 3287 | 152 | 17,687 | 0 |
| pubmedqa | 405 | 1168 | 1963 | 420 | 210,084 | 0 |
| rewardbench2 | 642 | 1160 | 1649 | 1660 | 1,991,649 | 0 |
| scienceqa_text | 372 | 542 | 949 | 104 | 103,717 | 0 |
| scifact_rank_choice | 875 | 1054 | 1133 | 2729 | 818,697 | 0 |
| scifact_rank_noul | 6530 | 8157 | 9075 | 62673 | 18,801,780 | 0 |
| sst5 | 388 | 4960 | 5569 | 87 | 43,646 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** nfcorpus_rank_choice: 10. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-liquid-d1-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

