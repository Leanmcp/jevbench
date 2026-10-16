# jev-bench results: or-cloudflare-clef-full

Scored 2026-10-15T23:38:30-0700. Model requested `or-cloudflare-clef`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8320** | [0.796, 0.864] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7860** | [0.750, 0.822] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.9380** | [0.916, 0.958] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.9480** | [0.929, 0.967] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **0.9343** | [0.877, 0.997] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9700** | [0.953, 0.985] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9554** | [0.902, 1.000] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.5503** | [0.473, 0.627] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7250** | [0.688, 0.761] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8430** | [0.812, 0.872] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6680** | [0.631, 0.708] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3692** | [0.335, 0.406] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3764** | [0.342, 0.413] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3732** | [0.337, 0.410] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.8017** | [0.724, 0.871] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6780** | [0.636, 0.718] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.6692** | [0.634, 0.701] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9390** | [0.921, 0.957] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7520** | [0.707, 0.795] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7448** | [0.700, 0.788] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5359** | [0.502, 0.572] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 94.8% | 0.9465 | 0.0802 | 0.2066 | 0 | 0.0428 | 1000 |
| mcpbench_server_routing | 112 | 28 | 95.5% | 0.9415 | 0.0590 | 0.1728 | 0 | 0.1084 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0216 | 0.1020 | 0 | 0.0917 | 26 |
| mcpmark_server_routing | 338 | 8 | 55.0% | 0.4886 | 0.6189 | 1.2868 | 0 | 0.1915 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0008 | 0.0216 | 0 | 0.0213 | 18 |
| medmcqa | 1000 | 4 | 72.5% | 0.7253 | 0.3733 | 0.7004 | 0 | 0.0656 | 1000 |
| medqa_usmle | 1000 | 4 | 84.3% | 0.8427 | 0.2199 | 0.4220 | 0 | 0.0364 | 1000 |
| mmlu_pro | 1000 | 10 | 66.8% | 0.6644 | 0.4323 | 1.0117 | 0 | 0.0363 | 1000 |
| pubmedqa | 500 | 3 | 67.8% | 0.5819 | 0.4579 | 0.8138 | 0 | 0.1001 | 500 |
| rewardbench2 | 1200 | 4 | 66.9% | 0.6689 | 0.4792 | 0.9085 | 0 | 0.1379 | 1200 |
| scienceqa_text | 1000 | 4 | 93.9% | 0.9593 | 0.0945 | 0.1682 | 0 | 0.0096 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 83.2% | 16.8% | 88.4% | 22.0% | 0.9226 | 0.1235 | 0.0620 | 50.0% |
| aegis2_response | 500 | 78.6% | 21.4% | 92.4% | 35.2% | 0.8912 | 0.1498 | 0.0489 | 50.0% |
| atbench500 | 500 | 93.8% | 6.2% | 98.8% | 11.2% | 0.9860 | 0.0580 | 0.0801 | 50.0% |
| jailbreak_classification | 400 | 97.0% | 3.0% | 91.5% | 0.0% | 0.9977 | 0.0211 | 0.0158 | 35.2% |
| prompt_injections | 116 | 80.2% | 19.8% | 61.7% | 0.0% | 0.9943 | 0.1417 | 0.1140 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 32.0% | 80.0% | 0.934 | 0.1617 | 0.510 |
| nfcorpus_rank_graded | 4924 | 3 | 63.0% | 96.5% | 0.464 | 0.1362 | 0.486 |
| sst5 | 500 | 5 | 53.6% | 97.6% | 0.536 | 0.0831 | 0.883 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3692 | 0.6199 | 0.1705 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3764 | 0.6177 | 0.1749 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3732 | 0.6166 | 0.1727 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7520 | 0.7376 | 0.8251 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7448 | 0.7293 | 0.8217 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 67.9% |
| rewardbench2 | Focus | 240 | 70.0% |
| rewardbench2 | Math | 240 | 75.0% |
| rewardbench2 | Precise IF | 240 | 32.9% |
| rewardbench2 | Safety | 240 | 88.8% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 94.6% | 95.0% | 94.6% | 0.4% |
| mcpbench_server_routing | 56 | 94.6% | 96.4% | 94.6% | 1.8% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 54.4% | 55.6% | 54.4% | 1.2% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 72.0% | 73.0% | 66.0% | 13.0% |
| medqa_usmle | 500 | 84.8% | 83.8% | 80.8% | 7.0% |
| mmlu_pro | 500 | 67.4% | 66.2% | 60.8% | 12.0% |
| rewardbench2 | 594 | 67.2% | 66.7% | 58.1% | 17.7% |
| scienceqa_text | 500 | 94.2% | 93.6% | 91.4% | 5.0% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 394 | 824 | 1414 | 248 | 124,116 | 0 |
| aegis2_response | 372 | 620 | 1179 | 351 | 175,252 | 0 |
| atbench500 | 1000 | 5371 | 6185 | 1959 | 979,492 | 0 |
| banking77 | 887 | 1686 | 1998 | 1846 | 1,846,092 | 0 |
| helpsteer2_helpfulness | 698 | 5967 | 6531 | 752 | 375,942 | 0 |
| jailbreak_classification | 515 | 1178 | 1518 | 461 | 184,589 | 0 |
| mcpbench_server_routing | 619 | 1056 | 1810 | 997 | 111,660 | 0 |
| mcpbench_tool_selection | 550 | 990 | 1085 | 835 | 21,708 | 0 |
| mcpmark_server_routing | 540 | 1038 | 1564 | 323 | 109,126 | 0 |
| mcpmark_tool_selection | 526 | 1286 | 1286 | 469 | 8,448 | 0 |
| medmcqa | 503 | 758 | 1346 | 209 | 209,014 | 0 |
| medqa_usmle | 508 | 741 | 1385 | 374 | 373,536 | 0 |
| mmlu_pro | 500 | 775 | 1275 | 409 | 409,206 | 0 |
| nfcorpus_rank_choice | 2140 | 6450 | 6931 | 2526 | 752,758 | 0 |
| nfcorpus_rank_graded | 538 | 1648 | 2613 | 374 | 1,843,503 | 1 |
| nfcorpus_rank_noul | 1735 | 3913 | 4497 | 4765 | 1,419,832 | 0 |
| prompt_injections | 477 | 744 | 870 | 238 | 27,613 | 0 |
| pubmedqa | 509 | 845 | 1824 | 525 | 262,438 | 0 |
| rewardbench2 | 1042 | 2258 | 3038 | 1886 | 2,262,656 | 0 |
| scienceqa_text | 450 | 692 | 1060 | 194 | 194,026 | 0 |
| scifact_rank_choice | 1496 | 2563 | 3473 | 3169 | 950,821 | 0 |
| scifact_rank_noul | 1958 | 4449 | 5537 | 6014 | 1,804,128 | 0 |
| sst5 | 417 | 623 | 1547 | 208 | 103,769 | 0 |

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

Artifacts: `data/runs/or-cloudflare-clef-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

