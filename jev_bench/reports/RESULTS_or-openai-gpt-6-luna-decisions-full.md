# jev-bench results: or-openai-gpt-6-luna-decisions-full

Scored 2026-10-11T19:55:15-0700. Model requested `or-openai-gpt-6-luna-decisions`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.7480** | [0.710, 0.786] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7260** | [0.686, 0.766] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.8780** | [0.850, 0.906] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.7860** | [0.753, 0.818] | accuracy |
| helpsteer2_helpfulness | score | 500 | 99.8% | **0.9673** | [0.900, 1.036] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9675** | [0.950, 0.985] | accuracy |
| mcpbench_server_routing | choice | 112 | 97.3% | **0.9633** | [0.907, 1.000] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 99.4% | **0.4911** | [0.423, 0.560] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 98.3% | **0.7731** | [0.741, 0.806] | accuracy |
| medqa_usmle | choice | 1000 | 99.9% | **0.8759** | [0.849, 0.903] | accuracy |
| mmlu_pro | choice | 1000 | 99.5% | **0.5990** | [0.560, 0.637] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 93.6% | **0.3564** | [0.321, 0.395] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3648** | [0.332, 0.401] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3676** | [0.331, 0.403] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.6379** | [0.552, 0.724] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6280** | [0.586, 0.668] | accuracy |
| rewardbench2 | choice | 1200 | 96.1% | **0.7294** | [0.698, 0.762] | accuracy |
| scienceqa_text | choice | 1000 | 99.8% | **0.9409** | [0.923, 0.957] | accuracy |
| scifact_rank_choice | rank | 300 | 99.0% | **0.7494** | [0.706, 0.790] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7293** | [0.682, 0.776] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5424** | [0.498, 0.587] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 78.6% | 0.7704 | 0.3301 | 0.5726 | 49 | 0.0798 | 1000 |
| mcpbench_server_routing | 109 | 28 | 96.3% | 0.9631 | 0.0638 | 0.1525 | 0 | 0.0683 | 109 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0017 | 0.0191 | 0 | 0.0185 | 26 |
| mcpmark_server_routing | 336 | 8 | 49.1% | 0.4268 | 0.6792 | 1.4334 | 6 | 0.1565 | 336 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0000 | 0.0022 | 0 | 0.0022 | 18 |
| medmcqa | 983 | 4 | 77.3% | 0.7731 | 0.3230 | 0.5910 | 5 | 0.0793 | 983 |
| medqa_usmle | 999 | 4 | 87.6% | 0.8762 | 0.1779 | 0.3143 | 5 | 0.0508 | 999 |
| mmlu_pro | 995 | 10 | 59.9% | 0.5958 | 0.5356 | 1.2030 | 15 | 0.0701 | 995 |
| pubmedqa | 500 | 3 | 62.8% | 0.5861 | 0.6238 | 0.8298 | 58 | 0.2628 | 500 |
| rewardbench2 | 1153 | 4 | 72.9% | 0.7281 | 0.3756 | 0.7282 | 4 | 0.0304 | 1153 |
| scienceqa_text | 998 | 4 | 94.1% | 0.9585 | 0.0755 | 0.1199 | 0 | 0.0142 | 998 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 74.8% | 25.2% | 51.2% | 1.6% | 0.8426 | 0.2342 | 0.2288 | 50.0% |
| aegis2_response | 500 | 72.6% | 27.4% | 50.4% | 5.2% | 0.8496 | 0.2431 | 0.2238 | 50.0% |
| atbench500 | 500 | 87.8% | 12.2% | 100.0% | 24.4% | 0.9710 | 0.0951 | 0.0681 | 50.0% |
| jailbreak_classification | 400 | 96.8% | 3.2% | 91.5% | 0.4% | 0.9782 | 0.0277 | 0.0228 | 35.2% |
| prompt_injections | 116 | 63.8% | 36.2% | 30.0% | 0.0% | 0.6708 | 0.3275 | 0.3086 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 499 | 5 | 32.3% | 78.0% | 0.967 | 0.1928 | 0.492 |
| nfcorpus_rank_graded | 4924 | 3 | 54.5% | 95.3% | 0.507 | 0.1818 | 0.488 |
| sst5 | 500 | 5 | 53.6% | 96.0% | 0.542 | 0.1028 | 0.849 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 279 | 0.3564 | 0.6198 | 0.1642 | 0.3362 | 0.4763 | 19.3% |
| nfcorpus_rank_graded | 298 | 0.3648 | 0.6087 | 0.1698 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3676 | 0.6113 | 0.1708 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 297 | 0.7494 | 0.7476 | 0.8062 | 0.6672 | 0.8384 | 83.4% |
| scifact_rank_noul | 300 | 0.7293 | 0.7191 | 0.7976 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 237 | 82.7% |
| rewardbench2 | Focus | 235 | 91.5% |
| rewardbench2 | Math | 231 | 62.8% |
| rewardbench2 | Precise IF | 236 | 37.7% |
| rewardbench2 | Safety | 214 | 91.6% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 79.6% | 77.6% | 74.2% | 8.8% |
| mcpbench_server_routing | 54 | 96.4% | 96.3% | 96.3% | 0.0% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 168 | 47.6% | 50.6% | 39.9% | 18.5% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 489 | 78.6% | 76.0% | 72.0% | 11.0% |
| medqa_usmle | 499 | 88.4% | 86.8% | 84.8% | 5.8% |
| mmlu_pro | 497 | 60.8% | 59.0% | 52.7% | 14.5% |
| rewardbench2 | 561 | 72.9% | 73.0% | 63.3% | 18.7% |
| scienceqa_text | 498 | 94.8% | 93.4% | 91.0% | 6.4% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 290 | 5048 | 5126 | 284 | 141,836 | 0 |
| aegis2_response | 269 | 602 | 1400 | 385 | 192,392 | 0 |
| atbench500 | 282 | 580 | 1640 | 1851 | 925,548 | 0 |
| banking77 | 262 | 401 | 1146 | 1000 | 999,872 | 0 |
| helpsteer2_helpfulness | 590 | 5257 | 5430 | 692 | 345,413 | 0 |
| jailbreak_classification | 280 | 404 | 1000 | 489 | 195,793 | 0 |
| mcpbench_server_routing | 319 | 535 | 1522 | 690 | 75,238 | 0 |
| mcpbench_tool_selection | 320 | 456 | 503 | 704 | 18,304 | 0 |
| mcpmark_server_routing | 313 | 496 | 1541 | 243 | 81,806 | 0 |
| mcpmark_tool_selection | 344 | 404 | 404 | 419 | 7,540 | 0 |
| medmcqa | 290 | 631 | 1294 | 173 | 170,039 | 0 |
| medqa_usmle | 249 | 338 | 979 | 328 | 328,083 | 0 |
| mmlu_pro | 246 | 367 | 568 | 311 | 309,058 | 0 |
| nfcorpus_rank_choice | 554 | 4935 | 5546 | 2324 | 648,389 | 0 |
| nfcorpus_rank_graded | 384 | 1094 | 1638 | 337 | 1,661,568 | 1 |
| nfcorpus_rank_noul | 482 | 982 | 1161 | 6057 | 1,804,853 | 0 |
| prompt_injections | 260 | 335 | 357 | 274 | 31,734 | 0 |
| pubmedqa | 252 | 478 | 588 | 482 | 240,774 | 0 |
| rewardbench2 | 502 | 1128 | 1658 | 1734 | 1,999,463 | 0 |
| scienceqa_text | 244 | 329 | 534 | 174 | 173,865 | 0 |
| scifact_rank_choice | 320 | 743 | 886 | 2845 | 844,825 | 0 |
| scifact_rank_noul | 452 | 1805 | 2010 | 7593 | 2,277,780 | 0 |
| sst5 | 240 | 306 | 403 | 153 | 76,596 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** helpsteer2_helpfulness: 1, mcpbench_server_routing: 3, mcpmark_server_routing: 2, medmcqa: 17, medqa_usmle: 1, mmlu_pro: 5, nfcorpus_rank_choice: 19, rewardbench2: 47, scienceqa_text: 2, scifact_rank_choice: 3. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-openai-gpt-6-luna-decisions-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

