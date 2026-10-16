# jev-bench results: or-scaledown-classify-1-full

Scored 2026-10-15T08:14:53-0700. Model requested `or-scaledown-classify-1`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8280** | [0.794, 0.860] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7500** | [0.712, 0.788] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.5200** | [0.478, 0.564] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.7360** | [0.703, 0.770] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.0785** | [1.004, 1.157] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9550** | [0.932, 0.975] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.8571** | [0.777, 0.929] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4320** | [0.361, 0.503] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.5960** | [0.555, 0.633] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.7420** | [0.707, 0.776] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.4360** | [0.397, 0.475] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3467** | [0.314, 0.381] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3386** | [0.307, 0.373] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3119** | [0.280, 0.346] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.8879** | [0.828, 0.940] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.5440** | [0.500, 0.588] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.6783** | [0.645, 0.710] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.8400** | [0.814, 0.865] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7088** | [0.664, 0.754] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.5661** | [0.521, 0.610] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.6171** | [0.580, 0.653] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 73.6% | 0.7206 | 0.4005 | 1.1751 | 0 | 0.1305 | 1000 |
| mcpbench_server_routing | 112 | 28 | 85.7% | 0.8410 | 0.2935 | 0.7575 | 0 | 0.2465 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.1582 | 0.4008 | 0 | 0.2905 | 26 |
| mcpmark_server_routing | 338 | 8 | 43.2% | 0.3412 | 0.7136 | 1.6697 | 0 | 0.1460 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0091 | 0.0607 | 0 | 0.0567 | 18 |
| medmcqa | 1000 | 4 | 59.6% | 0.5937 | 0.5058 | 0.9523 | 0 | 0.0608 | 1000 |
| medqa_usmle | 1000 | 4 | 74.2% | 0.7423 | 0.3776 | 0.7398 | 0 | 0.0986 | 1000 |
| mmlu_pro | 1000 | 10 | 43.6% | 0.4387 | 0.6688 | 1.6635 | 0 | 0.0621 | 1000 |
| pubmedqa | 500 | 3 | 54.4% | 0.5291 | 0.5639 | 0.9330 | 0 | 0.0845 | 500 |
| rewardbench2 | 1200 | 4 | 67.8% | 0.6783 | 0.4438 | 0.8530 | 0 | 0.0575 | 1200 |
| scienceqa_text | 1000 | 4 | 84.0% | 0.8357 | 0.2150 | 0.3678 | 0 | 0.0779 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 82.8% | 17.2% | 76.8% | 11.2% | 0.9016 | 0.1459 | 0.1440 | 50.0% |
| aegis2_response | 500 | 75.0% | 25.0% | 79.6% | 29.6% | 0.8213 | 0.2122 | 0.1821 | 50.0% |
| atbench500 | 500 | 52.0% | 48.0% | 91.2% | 87.2% | 0.5172 | 0.2599 | 0.0842 | 50.0% |
| jailbreak_classification | 400 | 95.5% | 4.5% | 92.9% | 3.1% | 0.9845 | 0.1007 | 0.2471 | 35.2% |
| prompt_injections | 116 | 88.8% | 11.2% | 78.3% | 0.0% | 0.9811 | 0.1138 | 0.1862 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 27.2% | 75.4% | 1.078 | 0.1909 | 0.402 |
| nfcorpus_rank_graded | 4924 | 3 | 30.4% | 89.7% | 0.816 | 0.2658 | 0.415 |
| sst5 | 500 | 5 | 41.4% | 98.0% | 0.617 | 0.0961 | 0.862 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3467 | 0.6089 | 0.1623 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3386 | 0.5511 | 0.1698 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3119 | 0.5459 | 0.1502 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7088 | 0.6891 | 0.8026 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.5661 | 0.5244 | 0.7278 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 65.4% |
| rewardbench2 | Focus | 240 | 94.2% |
| rewardbench2 | Math | 240 | 61.7% |
| rewardbench2 | Precise IF | 240 | 39.6% |
| rewardbench2 | Safety | 240 | 78.3% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 74.2% | 73.0% | 65.8% | 15.6% |
| mcpbench_server_routing | 56 | 85.7% | 85.7% | 76.8% | 17.9% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 45.0% | 41.4% | 37.3% | 11.8% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 60.4% | 58.8% | 48.4% | 22.4% |
| medqa_usmle | 500 | 75.0% | 73.4% | 65.8% | 16.8% |
| mmlu_pro | 500 | 42.6% | 44.6% | 34.6% | 18.0% |
| rewardbench2 | 594 | 66.7% | 69.0% | 57.7% | 20.2% |
| scienceqa_text | 500 | 85.6% | 82.4% | 74.6% | 18.8% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 428 | 1075 | 1913 | 347 | 173,616 | 0 |
| aegis2_response | 407 | 771 | 1407 | 450 | 224,847 | 0 |
| atbench500 | 448 | 827 | 1186 | 2061 | 1,030,599 | 0 |
| banking77 | 620 | 1176 | 2001 | 3614 | 3,614,268 | 0 |
| helpsteer2_helpfulness | 447 | 868 | 1429 | 876 | 437,942 | 0 |
| jailbreak_classification | 393 | 786 | 1906 | 562 | 224,989 | 0 |
| mcpbench_server_routing | 539 | 1113 | 1306 | 2497 | 279,685 | 0 |
| mcpbench_tool_selection | 397 | 563 | 596 | 1107 | 28,792 | 0 |
| mcpmark_server_routing | 391 | 603 | 867 | 414 | 139,884 | 0 |
| mcpmark_tool_selection | 408 | 712 | 712 | 634 | 11,418 | 0 |
| medmcqa | 376 | 618 | 1430 | 318 | 318,088 | 0 |
| medqa_usmle | 386 | 766 | 1633 | 489 | 488,760 | 0 |
| mmlu_pro | 382 | 562 | 1083 | 587 | 586,896 | 0 |
| nfcorpus_rank_choice | 657 | 966 | 1392 | 8301 | 2,473,705 | 0 |
| nfcorpus_rank_graded | 420 | 1376 | 2847 | 503 | 2,475,489 | 3 |
| nfcorpus_rank_noul | 2224 | 5061 | 5382 | 47864 | 14,263,603 | 0 |
| prompt_injections | 413 | 752 | 1577 | 336 | 38,981 | 0 |
| pubmedqa | 389 | 907 | 1728 | 654 | 326,938 | 0 |
| rewardbench2 | 457 | 767 | 1640 | 3515 | 4,218,082 | 0 |
| scienceqa_text | 402 | 766 | 1548 | 309 | 308,562 | 0 |
| scifact_rank_choice | 743 | 1484 | 2134 | 10904 | 3,271,180 | 0 |
| scifact_rank_noul | 2762 | 5193 | 5384 | 63126 | 18,937,700 | 0 |
| sst5 | 420 | 798 | 1399 | 307 | 153,269 | 0 |

Measured end to end from this client at concurrency 8, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-scaledown-classify-1-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

