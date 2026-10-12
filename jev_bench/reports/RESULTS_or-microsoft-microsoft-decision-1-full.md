# jev-bench results: or-microsoft-microsoft-decision-1-full

Scored 2026-10-11T19:56:49-0700. Model requested `or-microsoft-microsoft-decision-1`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8200** | [0.784, 0.852] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.8220** | [0.788, 0.856] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.8680** | [0.838, 0.898] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8640** | [0.834, 0.893] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **0.9012** | [0.835, 0.974] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9650** | [0.948, 0.980] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9464** | [0.875, 1.000] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4882** | [0.417, 0.565] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7590** | [0.722, 0.792] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8070** | [0.776, 0.839] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6470** | [0.609, 0.686] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 96.6% | **0.3644** | [0.330, 0.399] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3732** | [0.339, 0.411] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3680** | [0.332, 0.404] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.7328** | [0.647, 0.819] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6800** | [0.640, 0.720] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.7492** | [0.718, 0.779] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9320** | [0.911, 0.951] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7370** | [0.693, 0.780] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7302** | [0.684, 0.773] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5418** | [0.505, 0.583] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 86.4% | 0.8590 | 0.1896 | 0.4587 | 0 | 0.0235 | 1000 |
| mcpbench_server_routing | 112 | 28 | 94.6% | 0.9421 | 0.0844 | 0.1893 | 0 | 0.0215 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0001 | 0.0036 | 0 | 0.0036 | 26 |
| mcpmark_server_routing | 338 | 8 | 48.8% | 0.4185 | 0.7481 | 1.8351 | 0 | 0.2566 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0000 | 0.0015 | 0 | 0.0015 | 18 |
| medmcqa | 1000 | 4 | 75.9% | 0.7594 | 0.3380 | 0.6393 | 0 | 0.0519 | 1000 |
| medqa_usmle | 1000 | 4 | 80.7% | 0.8073 | 0.2791 | 0.5275 | 0 | 0.0604 | 1000 |
| mmlu_pro | 1000 | 10 | 64.7% | 0.6449 | 0.4933 | 1.1581 | 0 | 0.0643 | 1000 |
| pubmedqa | 500 | 3 | 68.0% | 0.6013 | 0.4974 | 0.9720 | 0 | 0.1597 | 500 |
| rewardbench2 | 1200 | 4 | 74.9% | 0.7494 | 0.3556 | 0.6922 | 0 | 0.0207 | 1200 |
| scienceqa_text | 1000 | 4 | 93.2% | 0.9490 | 0.0896 | 0.1496 | 0 | 0.0137 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 82.0% | 18.0% | 71.6% | 7.6% | 0.9116 | 0.1334 | 0.0621 | 50.0% |
| aegis2_response | 500 | 82.2% | 17.8% | 81.6% | 17.2% | 0.9011 | 0.1295 | 0.0234 | 50.0% |
| atbench500 | 500 | 86.8% | 13.2% | 74.0% | 0.4% | 0.9928 | 0.0877 | 0.0330 | 50.0% |
| jailbreak_classification | 400 | 96.5% | 3.5% | 97.2% | 3.9% | 0.9939 | 0.0317 | 0.0321 | 35.2% |
| prompt_injections | 116 | 73.3% | 26.7% | 48.3% | 0.0% | 0.9875 | 0.1993 | 0.1845 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 35.0% | 81.4% | 0.901 | 0.1591 | 0.566 |
| nfcorpus_rank_graded | 4924 | 3 | 71.0% | 97.9% | 0.345 | 0.1198 | 0.490 |
| sst5 | 500 | 5 | 56.0% | 97.4% | 0.542 | 0.0866 | 0.874 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 288 | 0.3644 | 0.6069 | 0.1669 | 0.3295 | 0.4673 | 18.8% |
| nfcorpus_rank_graded | 298 | 0.3732 | 0.6119 | 0.1727 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3680 | 0.6080 | 0.1719 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7370 | 0.7230 | 0.8101 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7302 | 0.7119 | 0.8134 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 69.2% |
| rewardbench2 | Focus | 240 | 94.2% |
| rewardbench2 | Math | 240 | 73.8% |
| rewardbench2 | Precise IF | 240 | 45.4% |
| rewardbench2 | Safety | 240 | 92.1% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 86.6% | 86.2% | 85.8% | 1.2% |
| mcpbench_server_routing | 56 | 94.6% | 94.6% | 94.6% | 0.0% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 49.1% | 48.5% | 47.9% | 1.8% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 75.6% | 76.2% | 71.0% | 9.8% |
| medqa_usmle | 500 | 80.2% | 81.2% | 76.8% | 7.8% |
| mmlu_pro | 500 | 64.6% | 64.8% | 58.0% | 13.4% |
| rewardbench2 | 594 | 75.0% | 74.8% | 66.5% | 16.3% |
| scienceqa_text | 500 | 93.2% | 93.2% | 90.8% | 4.8% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 350 | 5903 | 6005 | 154 | 77,116 | 0 |
| aegis2_response | 319 | 417 | 508 | 257 | 128,347 | 0 |
| atbench500 | 373 | 552 | 1029 | 1864 | 932,099 | 1 |
| banking77 | 426 | 705 | 1057 | 783 | 783,092 | 0 |
| helpsteer2_helpfulness | 376 | 5164 | 5240 | 611 | 305,442 | 0 |
| jailbreak_classification | 368 | 604 | 1390 | 367 | 146,991 | 0 |
| mcpbench_server_routing | 354 | 462 | 1070 | 570 | 63,836 | 0 |
| mcpbench_tool_selection | 330 | 417 | 544 | 604 | 15,714 | 0 |
| mcpmark_server_routing | 317 | 400 | 472 | 155 | 52,342 | 0 |
| mcpmark_tool_selection | 312 | 387 | 387 | 339 | 6,108 | 0 |
| medmcqa | 318 | 490 | 857 | 89 | 89,045 | 90 |
| medqa_usmle | 298 | 466 | 623 | 254 | 253,578 | 288 |
| mmlu_pro | 308 | 418 | 665 | 223 | 223,378 | 153 |
| nfcorpus_rank_choice | 503 | 5548 | 5596 | 2318 | 667,480 | 6 |
| nfcorpus_rank_graded | 335 | 679 | 1275 | 262 | 1,288,805 | 303 |
| nfcorpus_rank_noul | 521 | 759 | 940 | 4044 | 1,205,060 | 23 |
| prompt_injections | 298 | 373 | 415 | 144 | 16,709 | 13 |
| pubmedqa | 310 | 382 | 598 | 419 | 209,438 | 37 |
| rewardbench2 | 348 | 669 | 1262 | 1766 | 2,119,565 | 89 |
| scienceqa_text | 298 | 386 | 619 | 93 | 93,215 | 84 |
| scifact_rank_choice | 359 | 571 | 768 | 2846 | 853,922 | 20 |
| scifact_rank_noul | 548 | 746 | 1088 | 5153 | 1,545,985 | 13 |
| sst5 | 292 | 371 | 421 | 67 | 33,269 | 38 |

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

Artifacts: `data/runs/or-microsoft-microsoft-decision-1-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

