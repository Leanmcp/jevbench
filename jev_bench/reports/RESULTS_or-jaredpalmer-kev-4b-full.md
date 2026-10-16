# jev-bench results: or-jaredpalmer-kev-4b-full

Scored 2026-10-15T23:48:04-0700. Model requested `or-jaredpalmer-kev-4b`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8400** | [0.808, 0.872] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7940** | [0.758, 0.830] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.4860** | [0.444, 0.528] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8530** | [0.821, 0.882] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.0833** | [1.011, 1.156] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9475** | [0.925, 0.968] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.8125** | [0.705, 0.902] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **0.7308** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.5000** | [0.429, 0.571] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.5640** | [0.524, 0.604] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.6720** | [0.634, 0.708] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.5270** | [0.487, 0.566] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3515** | [0.318, 0.387] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3574** | [0.324, 0.395] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3509** | [0.316, 0.386] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.5948** | [0.500, 0.681] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6460** | [0.604, 0.688] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.6325** | [0.600, 0.665] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.8690** | [0.842, 0.895] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7143** | [0.671, 0.758] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7129** | [0.670, 0.755] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5406** | [0.504, 0.581] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 85.3% | 0.8425 | 0.2554 | 0.6438 | 0 | 0.1328 | 1000 |
| mcpbench_server_routing | 112 | 28 | 81.2% | 0.7742 | 0.4044 | 0.9480 | 0 | 0.3416 | 112 |
| mcpbench_tool_selection | 26 | 13 | 73.1% | 0.6946 | 0.4717 | 0.9655 | 0 | 0.3499 | 26 |
| mcpmark_server_routing | 338 | 8 | 50.0% | 0.4920 | 0.6830 | 1.4907 | 0 | 0.0942 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0661 | 0.2114 | 0 | 0.1792 | 18 |
| medmcqa | 1000 | 4 | 56.4% | 0.5641 | 0.5214 | 0.9799 | 0 | 0.0529 | 1000 |
| medqa_usmle | 1000 | 4 | 67.2% | 0.6715 | 0.4434 | 0.8183 | 0 | 0.0460 | 1000 |
| mmlu_pro | 1000 | 10 | 52.7% | 0.5252 | 0.5956 | 1.3796 | 0 | 0.0610 | 1000 |
| pubmedqa | 500 | 3 | 64.6% | 0.5680 | 0.4741 | 0.8083 | 0 | 0.0796 | 500 |
| rewardbench2 | 1200 | 4 | 63.2% | 0.6345 | 0.5244 | 0.9914 | 0 | 0.1620 | 1200 |
| scienceqa_text | 1000 | 4 | 86.9% | 0.8747 | 0.1679 | 0.2783 | 0 | 0.0348 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 84.0% | 16.0% | 81.2% | 13.2% | 0.9242 | 0.1111 | 0.0396 | 50.0% |
| aegis2_response | 500 | 79.4% | 20.6% | 70.4% | 11.6% | 0.8861 | 0.1454 | 0.0269 | 50.0% |
| atbench500 | 500 | 48.6% | 51.4% | 71.6% | 74.4% | 0.5334 | 0.2813 | 0.1710 | 50.0% |
| jailbreak_classification | 400 | 94.8% | 5.2% | 87.9% | 1.5% | 0.9935 | 0.0433 | 0.0782 | 35.2% |
| prompt_injections | 116 | 59.5% | 40.5% | 21.7% | 0.0% | 0.9479 | 0.2721 | 0.2696 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 26.2% | 72.2% | 1.083 | 0.1870 | 0.333 |
| nfcorpus_rank_graded | 4924 | 3 | 45.3% | 92.0% | 0.650 | 0.2124 | 0.416 |
| sst5 | 500 | 5 | 56.4% | 96.6% | 0.541 | 0.0865 | 0.870 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3515 | 0.5843 | 0.1691 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3574 | 0.5942 | 0.1722 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3509 | 0.5658 | 0.1712 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7143 | 0.6899 | 0.8067 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7129 | 0.6897 | 0.8117 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 50.8% |
| rewardbench2 | Focus | 240 | 90.4% |
| rewardbench2 | Math | 240 | 61.7% |
| rewardbench2 | Precise IF | 240 | 31.7% |
| rewardbench2 | Safety | 240 | 81.7% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 85.6% | 85.0% | 83.2% | 4.2% |
| mcpbench_server_routing | 56 | 80.4% | 82.1% | 78.6% | 5.4% |
| mcpbench_tool_selection | 4 | 76.9% | 69.2% | 75.0% | 0.0% |
| mcpmark_server_routing | 169 | 50.9% | 49.1% | 47.3% | 5.3% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 54.8% | 58.0% | 48.8% | 15.2% |
| medqa_usmle | 500 | 66.6% | 67.8% | 60.6% | 13.2% |
| mmlu_pro | 500 | 52.2% | 53.2% | 44.2% | 17.0% |
| rewardbench2 | 594 | 64.3% | 62.2% | 52.4% | 22.6% |
| scienceqa_text | 500 | 86.4% | 87.4% | 82.8% | 8.2% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 3179 | 6614 | 6992 | 141 | 70,285 | 0 |
| aegis2_response | 3344 | 5149 | 6186 | 244 | 121,924 | 0 |
| atbench500 | 15152 | 21796 | 22359 | 1819 | 909,595 | 0 |
| banking77 | 5736 | 7844 | 11072 | 832 | 832,078 | 0 |
| helpsteer2_helpfulness | 7262 | 11713 | 14448 | 592 | 295,779 | 0 |
| jailbreak_classification | 5220 | 6947 | 7144 | 351 | 140,523 | 0 |
| mcpbench_server_routing | 4851 | 6134 | 6449 | 574 | 64,272 | 0 |
| mcpbench_tool_selection | 3913 | 4477 | 4479 | 612 | 15,916 | 0 |
| mcpmark_server_routing | 1915 | 3469 | 4464 | 146 | 49,278 | 0 |
| mcpmark_tool_selection | 2273 | 3021 | 3021 | 328 | 5,906 | 0 |
| medmcqa | 2272 | 3121 | 3785 | 79 | 78,526 | 0 |
| medqa_usmle | 2194 | 13132 | 15896 | 243 | 242,746 | 0 |
| mmlu_pro | 2274 | 3063 | 3668 | 222 | 222,228 | 0 |
| nfcorpus_rank_choice | 14154 | 21090 | 21208 | 2244 | 668,760 | 0 |
| nfcorpus_rank_graded | 1588 | 3791 | 8402 | 252 | 1,238,919 | 80 |
| nfcorpus_rank_noul | 14175 | 31094 | 38034 | 3943 | 1,174,886 | 0 |
| prompt_injections | 1524 | 2278 | 2472 | 131 | 15,165 | 0 |
| pubmedqa | 2121 | 2915 | 3272 | 419 | 209,318 | 0 |
| rewardbench2 | 6878 | 13605 | 26678 | 1715 | 2,058,346 | 0 |
| scienceqa_text | 1218 | 1979 | 2670 | 82 | 81,660 | 0 |
| scifact_rank_choice | 9793 | 19302 | 19326 | 2849 | 854,593 | 0 |
| scifact_rank_noul | 13572 | 32002 | 34915 | 5035 | 1,510,419 | 0 |
| sst5 | 1076 | 2895 | 3399 | 56 | 28,203 | 0 |

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

Artifacts: `data/runs/or-jaredpalmer-kev-4b-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

