# jev-bench results: or-perplexity-pplx-decider-v1.1-27b-full

Scored 2026-10-11T19:53:43-0700. Model requested `or-perplexity-pplx-decider-v1.1-27b`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8600** | [0.830, 0.890] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.8080** | [0.772, 0.842] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7460** | [0.710, 0.784] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8180** | [0.783, 0.849] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **0.8689** | [0.811, 0.933] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.8975** | [0.865, 0.927] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9821** | [0.955, 1.000] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.5799** | [0.512, 0.654] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7570** | [0.722, 0.792] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8890** | [0.863, 0.915] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.7080** | [0.669, 0.745] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3665** | [0.332, 0.399] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3777** | [0.344, 0.415] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3814** | [0.346, 0.417] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.9052** | [0.853, 0.957] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6960** | [0.656, 0.736] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.8150** | [0.785, 0.844] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9700** | [0.956, 0.983] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7535** | [0.709, 0.795] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7558** | [0.713, 0.797] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5078** | [0.474, 0.543] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 81.8% | 0.8043 | 0.2825 | 0.7910 | 0 | 0.0552 | 1000 |
| mcpbench_server_routing | 112 | 28 | 98.2% | 0.9819 | 0.0339 | 0.0655 | 0 | 0.0314 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0000 | 0.0008 | 0 | 0.0008 | 26 |
| mcpmark_server_routing | 338 | 8 | 58.0% | 0.5470 | 0.5931 | 1.2920 | 0 | 0.1719 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0000 | 0.0003 | 0 | 0.0003 | 18 |
| medmcqa | 1000 | 4 | 75.7% | 0.7569 | 0.3294 | 0.6352 | 0 | 0.0898 | 1000 |
| medqa_usmle | 1000 | 4 | 88.9% | 0.8889 | 0.1607 | 0.3081 | 0 | 0.0288 | 1000 |
| mmlu_pro | 1000 | 10 | 70.8% | 0.7083 | 0.4031 | 0.9284 | 0 | 0.0714 | 1000 |
| pubmedqa | 500 | 3 | 69.6% | 0.6390 | 0.4193 | 0.7188 | 0 | 0.0785 | 500 |
| rewardbench2 | 1200 | 4 | 81.5% | 0.8147 | 0.2539 | 0.5117 | 0 | 0.0410 | 1200 |
| scienceqa_text | 1000 | 4 | 97.0% | 0.9808 | 0.0463 | 0.0762 | 0 | 0.0092 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 86.0% | 14.0% | 80.8% | 8.8% | 0.9495 | 0.0997 | 0.0670 | 50.0% |
| aegis2_response | 500 | 80.8% | 19.2% | 68.0% | 6.4% | 0.9129 | 0.1527 | 0.1155 | 50.0% |
| atbench500 | 500 | 74.6% | 25.4% | 51.6% | 2.4% | 0.9686 | 0.1876 | 0.1668 | 50.0% |
| jailbreak_classification | 400 | 89.8% | 10.2% | 98.6% | 15.1% | 0.9919 | 0.0771 | 0.0517 | 35.2% |
| prompt_injections | 116 | 90.5% | 9.5% | 81.7% | 0.0% | 0.9902 | 0.0777 | 0.0594 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 34.0% | 86.4% | 0.869 | 0.1430 | 0.641 |
| nfcorpus_rank_graded | 4924 | 3 | 72.5% | 97.7% | 0.354 | 0.1110 | 0.489 |
| sst5 | 500 | 5 | 57.0% | 97.8% | 0.508 | 0.0812 | 0.891 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3665 | 0.6181 | 0.1703 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3777 | 0.6207 | 0.1751 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3814 | 0.6407 | 0.1732 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7535 | 0.7393 | 0.8234 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7558 | 0.7420 | 0.8259 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 79.6% |
| rewardbench2 | Focus | 240 | 95.0% |
| rewardbench2 | Math | 240 | 82.5% |
| rewardbench2 | Precise IF | 240 | 55.4% |
| rewardbench2 | Safety | 240 | 95.0% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 81.8% | 81.8% | 79.4% | 4.8% |
| mcpbench_server_routing | 56 | 96.4% | 100.0% | 96.4% | 3.6% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 59.8% | 56.2% | 55.0% | 5.9% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 76.2% | 75.2% | 72.8% | 5.8% |
| medqa_usmle | 500 | 89.2% | 88.6% | 86.4% | 5.0% |
| mmlu_pro | 500 | 71.0% | 70.6% | 67.4% | 6.8% |
| rewardbench2 | 594 | 81.2% | 81.8% | 77.8% | 7.6% |
| scienceqa_text | 500 | 96.8% | 97.2% | 96.4% | 1.2% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 395 | 5136 | 5202 | 206 | 103,112 | 0 |
| aegis2_response | 443 | 1387 | 2127 | 310 | 155,004 | 0 |
| atbench500 | 518 | 1147 | 1909 | 1966 | 983,180 | 0 |
| banking77 | 411 | 809 | 1324 | 964 | 964,090 | 0 |
| helpsteer2_helpfulness | 394 | 4534 | 4640 | 679 | 339,741 | 0 |
| jailbreak_classification | 466 | 1097 | 1765 | 419 | 167,703 | 0 |
| mcpbench_server_routing | 538 | 910 | 1108 | 669 | 74,924 | 0 |
| mcpbench_tool_selection | 677 | 751 | 1404 | 693 | 18,016 | 0 |
| mcpmark_server_routing | 389 | 603 | 1342 | 218 | 73,636 | 0 |
| mcpmark_tool_selection | 377 | 437 | 437 | 408 | 7,340 | 0 |
| medmcqa | 369 | 453 | 1855 | 150 | 149,596 | 0 |
| medqa_usmle | 377 | 482 | 664 | 314 | 313,916 | 0 |
| mmlu_pro | 375 | 457 | 531 | 299 | 298,818 | 0 |
| nfcorpus_rank_choice | 519 | 5184 | 5351 | 2399 | 691,028 | 0 |
| nfcorpus_rank_graded | 394 | 658 | 1302 | 321 | 1,582,912 | 1 |
| nfcorpus_rank_noul | 1409 | 2675 | 3399 | 47031 | 14,015,313 | 0 |
| prompt_injections | 369 | 440 | 472 | 196 | 22,739 | 0 |
| pubmedqa | 375 | 460 | 666 | 482 | 241,131 | 0 |
| rewardbench2 | 447 | 675 | 1012 | 1787 | 2,144,176 | 0 |
| scienceqa_text | 376 | 468 | 1011 | 152 | 151,638 | 0 |
| scifact_rank_choice | 467 | 633 | 878 | 2936 | 880,736 | 0 |
| scifact_rank_noul | 1538 | 2111 | 2696 | 62354 | 18,706,160 | 0 |
| sst5 | 366 | 445 | 639 | 129 | 64,254 | 0 |

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

Artifacts: `data/runs/or-perplexity-pplx-decider-v1.1-27b-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

