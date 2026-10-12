# jev-bench results: or-inception-mercury-decide-full

Scored 2026-10-11T20:01:00-0700. Model requested `or-inception-mercury-decide`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8400** | [0.808, 0.870] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7720** | [0.734, 0.810] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.6880** | [0.646, 0.730] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8990** | [0.875, 0.924] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **0.9469** | [0.878, 1.017] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9675** | [0.950, 0.983] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **1.0000** | [1.000, 1.000] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.5710** | [0.500, 0.645] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7260** | [0.691, 0.763] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8490** | [0.820, 0.877] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6450** | [0.606, 0.683] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3554** | [0.321, 0.389] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3673** | [0.333, 0.404] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3746** | [0.340, 0.412] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.8103** | [0.741, 0.879] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6560** | [0.616, 0.698] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.7933** | [0.763, 0.822] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9420** | [0.922, 0.960] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7255** | [0.682, 0.769] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7433** | [0.699, 0.787] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.4768** | [0.439, 0.516] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 89.9% | 0.8962 | 0.1670 | 0.4946 | 0 | 0.0637 | 1000 |
| mcpbench_server_routing | 112 | 28 | 100.0% | 1.0000 | 0.0140 | 0.0342 | 0 | 0.0236 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0000 | 0.0002 | 0 | 0.0002 | 26 |
| mcpmark_server_routing | 338 | 8 | 57.1% | 0.5157 | 0.6637 | 1.7849 | 0 | 0.2803 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0000 | 0.0001 | 0 | 0.0001 | 18 |
| medmcqa | 1000 | 4 | 72.6% | 0.7266 | 0.3953 | 0.7898 | 0 | 0.1374 | 1000 |
| medqa_usmle | 1000 | 4 | 84.9% | 0.8486 | 0.2433 | 0.4988 | 0 | 0.0816 | 1000 |
| mmlu_pro | 1000 | 10 | 64.5% | 0.6419 | 0.5369 | 1.3122 | 0 | 0.1796 | 1000 |
| pubmedqa | 500 | 3 | 65.6% | 0.6412 | 0.5671 | 1.0990 | 0 | 0.2184 | 500 |
| rewardbench2 | 1200 | 4 | 79.3% | 0.7932 | 0.3020 | 0.6393 | 0 | 0.0529 | 1200 |
| scienceqa_text | 1000 | 4 | 94.2% | 0.9665 | 0.0935 | 0.1716 | 0 | 0.0410 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 84.0% | 16.0% | 80.4% | 12.4% | 0.9279 | 0.1275 | 0.1109 | 50.0% |
| aegis2_response | 500 | 77.2% | 22.8% | 62.4% | 8.0% | 0.8876 | 0.1888 | 0.1655 | 50.0% |
| atbench500 | 500 | 68.8% | 31.2% | 37.6% | 0.0% | 0.9932 | 0.2794 | 0.2826 | 50.0% |
| jailbreak_classification | 400 | 96.8% | 3.2% | 90.8% | 0.0% | 0.9930 | 0.0301 | 0.0261 | 35.2% |
| prompt_injections | 116 | 81.0% | 19.0% | 63.3% | 0.0% | 0.9851 | 0.1570 | 0.1566 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 35.6% | 78.6% | 0.947 | 0.1763 | 0.555 |
| nfcorpus_rank_graded | 4924 | 3 | 78.0% | 97.1% | 0.278 | 0.1000 | 0.471 |
| sst5 | 500 | 5 | 59.4% | 97.6% | 0.477 | 0.0811 | 0.890 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3554 | 0.6219 | 0.1660 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3673 | 0.6026 | 0.1720 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3746 | 0.6220 | 0.1723 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7255 | 0.7071 | 0.8027 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7433 | 0.7255 | 0.8226 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 82.9% |
| rewardbench2 | Focus | 240 | 95.8% |
| rewardbench2 | Math | 240 | 77.1% |
| rewardbench2 | Precise IF | 240 | 47.9% |
| rewardbench2 | Safety | 240 | 92.9% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 90.4% | 89.4% | 88.0% | 3.8% |
| mcpbench_server_routing | 56 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 57.4% | 56.8% | 55.0% | 4.1% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 72.8% | 72.4% | 66.0% | 13.2% |
| medqa_usmle | 500 | 84.4% | 85.4% | 81.4% | 7.0% |
| mmlu_pro | 500 | 66.2% | 62.8% | 58.4% | 12.2% |
| rewardbench2 | 594 | 79.3% | 79.3% | 73.4% | 12.1% |
| scienceqa_text | 500 | 94.4% | 94.0% | 92.4% | 3.6% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 623 | 5289 | 6059 | 180 | 90,031 | 0 |
| aegis2_response | 564 | 1376 | 1831 | 282 | 140,800 | 0 |
| atbench500 | 851 | 1790 | 2262 | 1895 | 947,364 | 0 |
| banking77 | 854 | 1951 | 2792 | 1599 | 1,599,482 | 0 |
| helpsteer2_helpfulness | 924 | 6076 | 6843 | 670 | 335,063 | 0 |
| jailbreak_classification | 577 | 1288 | 1876 | 388 | 155,110 | 0 |
| mcpbench_server_routing | 852 | 1950 | 2237 | 867 | 97,113 | 0 |
| mcpbench_tool_selection | 773 | 2045 | 2180 | 755 | 19,632 | 0 |
| mcpmark_server_routing | 545 | 1223 | 1453 | 248 | 83,834 | 0 |
| mcpmark_tool_selection | 683 | 3488 | 3488 | 402 | 7,245 | 0 |
| medmcqa | 590 | 1329 | 1806 | 141 | 141,057 | 0 |
| medqa_usmle | 596 | 1546 | 2754 | 301 | 301,460 | 0 |
| mmlu_pro | 625 | 1712 | 2715 | 333 | 332,557 | 0 |
| nfcorpus_rank_choice | 1131 | 6996 | 7522 | 2380 | 709,228 | 0 |
| nfcorpus_rank_graded | 582 | 1449 | 2023 | 307 | 1,511,895 | 1 |
| nfcorpus_rank_noul | 2641 | 4668 | 5745 | 2399 | 715,032 | 0 |
| prompt_injections | 996 | 2094 | 3122 | 171 | 19,796 | 0 |
| pubmedqa | 1063 | 2672 | 3697 | 457 | 228,509 | 0 |
| rewardbench2 | 896 | 2057 | 2813 | 1777 | 2,132,815 | 0 |
| scienceqa_text | 896 | 2274 | 2831 | 129 | 129,244 | 0 |
| scifact_rank_choice | 1042 | 2422 | 2853 | 3003 | 901,036 | 3 |
| scifact_rank_noul | 3568 | 7529 | 8694 | 3020 | 905,961 | 312 |
| sst5 | 833 | 1986 | 2713 | 139 | 69,251 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-inception-mercury-decide-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

