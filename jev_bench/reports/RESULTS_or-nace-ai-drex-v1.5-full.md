# jev-bench results: or-nace-ai-drex-v1.5-full

Scored 2026-10-15T23:42:47-0700. Model requested `or-nace-ai-drex-v1.5`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.7920** | [0.756, 0.826] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7280** | [0.690, 0.768] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7700** | [0.734, 0.806] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8490** | [0.817, 0.879] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.0483** | [0.986, 1.124] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9200** | [0.892, 0.945] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9286** | [0.857, 0.982] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.3284** | [0.266, 0.391] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.6660** | [0.628, 0.706] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.7550** | [0.722, 0.789] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6100** | [0.570, 0.650] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3711** | [0.336, 0.408] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3746** | [0.339, 0.412] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3734** | [0.337, 0.411] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.5517** | [0.466, 0.638] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6520** | [0.610, 0.694] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.6933** | [0.661, 0.726] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9060** | [0.882, 0.930] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7361** | [0.692, 0.780] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7423** | [0.699, 0.785] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5590** | [0.521, 0.600] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 84.9% | 0.8422 | 0.2247 | 0.4936 | 0 | 0.0650 | 1000 |
| mcpbench_server_routing | 112 | 28 | 92.9% | 0.9173 | 0.1280 | 0.2776 | 0 | 0.0384 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0031 | 0.0270 | 0 | 0.0259 | 26 |
| mcpmark_server_routing | 338 | 8 | 32.8% | 0.3439 | 1.0033 | 2.4729 | 0 | 0.4216 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0006 | 0.0108 | 0 | 0.0107 | 18 |
| medmcqa | 1000 | 4 | 66.6% | 0.6659 | 0.4507 | 0.8569 | 0 | 0.0974 | 1000 |
| medqa_usmle | 1000 | 4 | 75.5% | 0.7558 | 0.3535 | 0.6647 | 0 | 0.0606 | 1000 |
| mmlu_pro | 1000 | 10 | 61.0% | 0.6118 | 0.5298 | 1.2948 | 0 | 0.1168 | 1000 |
| pubmedqa | 500 | 3 | 65.2% | 0.5623 | 0.5018 | 0.9060 | 0 | 0.1570 | 500 |
| rewardbench2 | 1200 | 4 | 69.3% | 0.6926 | 0.4215 | 0.8245 | 0 | 0.0674 | 1200 |
| scienceqa_text | 1000 | 4 | 90.6% | 0.9240 | 0.1297 | 0.2163 | 0 | 0.0299 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 79.2% | 20.8% | 61.2% | 2.8% | 0.8967 | 0.1782 | 0.1415 | 50.0% |
| aegis2_response | 500 | 72.8% | 27.2% | 56.4% | 10.8% | 0.8504 | 0.2010 | 0.1531 | 50.0% |
| atbench500 | 500 | 77.0% | 23.0% | 60.0% | 6.0% | 0.8932 | 0.1692 | 0.1121 | 50.0% |
| jailbreak_classification | 400 | 92.0% | 8.0% | 77.3% | 0.0% | 0.9915 | 0.0650 | 0.0562 | 35.2% |
| prompt_injections | 116 | 55.2% | 44.8% | 13.3% | 0.0% | 0.8921 | 0.4028 | 0.4162 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 28.0% | 75.4% | 1.048 | 0.1825 | 0.435 |
| nfcorpus_rank_graded | 4924 | 3 | 71.7% | 96.3% | 0.368 | 0.1136 | 0.486 |
| sst5 | 500 | 5 | 54.8% | 96.8% | 0.559 | 0.0900 | 0.863 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3711 | 0.6180 | 0.1729 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3746 | 0.6137 | 0.1740 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3734 | 0.6158 | 0.1731 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7361 | 0.7156 | 0.8217 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7423 | 0.7274 | 0.8192 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 63.7% |
| rewardbench2 | Focus | 240 | 89.6% |
| rewardbench2 | Math | 240 | 72.1% |
| rewardbench2 | Precise IF | 240 | 31.7% |
| rewardbench2 | Safety | 240 | 89.6% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 84.8% | 85.0% | 82.6% | 4.6% |
| mcpbench_server_routing | 56 | 92.9% | 92.9% | 91.1% | 3.6% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 36.7% | 29.0% | 26.6% | 12.4% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 66.4% | 66.8% | 60.4% | 12.4% |
| medqa_usmle | 500 | 75.4% | 75.6% | 71.0% | 9.0% |
| mmlu_pro | 500 | 60.4% | 61.6% | 54.4% | 13.2% |
| rewardbench2 | 594 | 70.7% | 68.0% | 62.1% | 14.6% |
| scienceqa_text | 500 | 91.6% | 89.6% | 87.8% | 5.6% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 986 | 6094 | 6405 | 141 | 70,285 | 0 |
| aegis2_response | 527 | 2179 | 2700 | 244 | 121,924 | 0 |
| atbench500 | 1670 | 2605 | 2837 | 1819 | 909,595 | 0 |
| banking77 | 535 | 1708 | 2240 | 832 | 832,078 | 0 |
| helpsteer2_helpfulness | 2090 | 7324 | 8175 | 592 | 295,779 | 0 |
| jailbreak_classification | 811 | 1652 | 2424 | 351 | 140,523 | 0 |
| mcpbench_server_routing | 1621 | 2389 | 2975 | 574 | 64,272 | 0 |
| mcpbench_tool_selection | 1894 | 2796 | 2829 | 612 | 15,916 | 0 |
| mcpmark_server_routing | 364 | 2139 | 2880 | 146 | 49,278 | 0 |
| mcpmark_tool_selection | 631 | 1092 | 1092 | 328 | 5,906 | 0 |
| medmcqa | 646 | 1843 | 2511 | 79 | 78,526 | 0 |
| medqa_usmle | 1354 | 2517 | 3074 | 243 | 242,746 | 0 |
| mmlu_pro | 1446 | 2805 | 3090 | 222 | 222,228 | 0 |
| nfcorpus_rank_choice | 2652 | 7341 | 8001 | 2244 | 668,760 | 1 |
| nfcorpus_rank_graded | 334 | 1162 | 2253 | 252 | 1,238,919 | 1 |
| nfcorpus_rank_noul | 2415 | 3227 | 4006 | 3943 | 1,174,886 | 0 |
| prompt_injections | 848 | 1848 | 2673 | 131 | 15,165 | 0 |
| pubmedqa | 822 | 2239 | 2475 | 419 | 209,318 | 0 |
| rewardbench2 | 3902 | 12040 | 17516 | 1715 | 2,058,346 | 356 |
| scienceqa_text | 502 | 1190 | 1801 | 82 | 81,660 | 0 |
| scifact_rank_choice | 4273 | 5480 | 5906 | 2849 | 854,593 | 112 |
| scifact_rank_noul | 4320 | 5832 | 6484 | 5035 | 1,510,419 | 109 |
| sst5 | 278 | 800 | 1803 | 56 | 28,203 | 0 |

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

Artifacts: `data/runs/or-nace-ai-drex-v1.5-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

