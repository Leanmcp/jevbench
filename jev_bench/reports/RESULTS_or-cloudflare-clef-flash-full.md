# jev-bench results: or-cloudflare-clef-flash-full

Scored 2026-10-11T19:50:17-0700. Model requested `or-cloudflare-clef-flash`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8320** | [0.798, 0.864] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7900** | [0.754, 0.826] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7680** | [0.732, 0.806] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.9610** | [0.944, 0.977] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.1446** | [1.063, 1.228] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9425** | [0.917, 0.965] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.8750** | [0.786, 0.946] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **0.9231** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4763** | [0.405, 0.553] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7040** | [0.667, 0.739] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.7660** | [0.730, 0.800] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6760** | [0.638, 0.713] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 98.7% | **0.3655** | [0.332, 0.402] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3787** | [0.345, 0.416] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3686** | [0.333, 0.404] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.5948** | [0.500, 0.681] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6960** | [0.654, 0.736] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.6000** | [0.564, 0.636] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9230** | [0.902, 0.944] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7376** | [0.693, 0.781] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7169** | [0.674, 0.761] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5321** | [0.496, 0.570] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 96.1% | 0.9598 | 0.0687 | 0.1875 | 0 | 0.0504 | 1000 |
| mcpbench_server_routing | 112 | 28 | 87.5% | 0.8645 | 0.1657 | 0.4159 | 0 | 0.1303 | 112 |
| mcpbench_tool_selection | 26 | 13 | 92.3% | 0.8974 | 0.0943 | 0.2129 | 0 | 0.0803 | 26 |
| mcpmark_server_routing | 338 | 8 | 47.6% | 0.5120 | 0.7204 | 1.5918 | 0 | 0.2033 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0046 | 0.0568 | 0 | 0.0549 | 18 |
| medmcqa | 1000 | 4 | 70.4% | 0.7037 | 0.4028 | 0.7631 | 0 | 0.0386 | 1000 |
| medqa_usmle | 1000 | 4 | 76.6% | 0.7658 | 0.3445 | 0.6575 | 0 | 0.0460 | 1000 |
| mmlu_pro | 1000 | 10 | 67.6% | 0.6727 | 0.4284 | 1.0351 | 0 | 0.0380 | 1000 |
| pubmedqa | 500 | 3 | 69.6% | 0.5647 | 0.4456 | 0.7917 | 0 | 0.1186 | 500 |
| rewardbench2 | 1200 | 4 | 60.0% | 0.6001 | 0.5502 | 1.0445 | 0 | 0.1047 | 1200 |
| scienceqa_text | 1000 | 4 | 92.3% | 0.9313 | 0.1142 | 0.2006 | 0 | 0.0291 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 83.2% | 16.8% | 81.6% | 15.2% | 0.9098 | 0.1218 | 0.0433 | 50.0% |
| aegis2_response | 500 | 79.0% | 21.0% | 74.0% | 16.0% | 0.8735 | 0.1546 | 0.0536 | 50.0% |
| atbench500 | 500 | 76.8% | 23.2% | 54.0% | 0.4% | 0.9419 | 0.1568 | 0.0890 | 50.0% |
| jailbreak_classification | 400 | 94.2% | 5.8% | 85.1% | 0.8% | 0.9883 | 0.0379 | 0.0453 | 35.2% |
| prompt_injections | 116 | 59.5% | 40.5% | 21.7% | 0.0% | 0.9860 | 0.3239 | 0.3299 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 25.2% | 72.0% | 1.145 | 0.2136 | 0.384 |
| nfcorpus_rank_graded | 4924 | 3 | 64.5% | 94.7% | 0.457 | 0.1398 | 0.488 |
| sst5 | 500 | 5 | 55.8% | 97.2% | 0.532 | 0.0837 | 0.878 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 294 | 0.3655 | 0.6173 | 0.1674 | 0.3311 | 0.4661 | 19.0% |
| nfcorpus_rank_graded | 298 | 0.3787 | 0.6326 | 0.1733 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3686 | 0.6165 | 0.1725 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7376 | 0.7168 | 0.8234 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7169 | 0.6962 | 0.8109 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 52.5% |
| rewardbench2 | Focus | 240 | 68.8% |
| rewardbench2 | Math | 240 | 66.7% |
| rewardbench2 | Precise IF | 240 | 31.2% |
| rewardbench2 | Safety | 240 | 80.8% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 96.2% | 96.0% | 96.0% | 0.2% |
| mcpbench_server_routing | 56 | 87.5% | 87.5% | 87.5% | 0.0% |
| mcpbench_tool_selection | 4 | 92.3% | 92.3% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 46.7% | 48.5% | 45.6% | 4.1% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 70.0% | 70.8% | 64.6% | 11.6% |
| medqa_usmle | 500 | 76.6% | 76.6% | 73.2% | 6.8% |
| mmlu_pro | 500 | 66.6% | 68.6% | 61.6% | 12.0% |
| rewardbench2 | 594 | 60.3% | 59.7% | 51.9% | 16.5% |
| scienceqa_text | 500 | 92.8% | 91.8% | 89.2% | 6.2% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 425 | 5089 | 5285 | 248 | 124,116 | 0 |
| aegis2_response | 364 | 630 | 1385 | 351 | 175,252 | 0 |
| atbench500 | 572 | 1048 | 1383 | 1959 | 979,492 | 0 |
| banking77 | 575 | 937 | 1804 | 1846 | 1,846,092 | 1 |
| helpsteer2_helpfulness | 409 | 6362 | 7155 | 752 | 375,942 | 0 |
| jailbreak_classification | 381 | 4865 | 5181 | 461 | 184,589 | 0 |
| mcpbench_server_routing | 409 | 583 | 976 | 997 | 111,660 | 0 |
| mcpbench_tool_selection | 382 | 542 | 1285 | 835 | 21,708 | 0 |
| mcpmark_server_routing | 350 | 465 | 862 | 323 | 109,126 | 0 |
| mcpmark_tool_selection | 343 | 574 | 574 | 469 | 8,448 | 0 |
| medmcqa | 380 | 578 | 803 | 209 | 209,014 | 0 |
| medqa_usmle | 415 | 628 | 1418 | 374 | 373,536 | 0 |
| mmlu_pro | 439 | 1047 | 1550 | 409 | 409,206 | 0 |
| nfcorpus_rank_choice | 1506 | 6022 | 7447 | 2556 | 751,563 | 0 |
| nfcorpus_rank_graded | 459 | 986 | 2951 | 374 | 1,843,503 | 0 |
| nfcorpus_rank_noul | 2212 | 15168 | 20004 | 4765 | 1,419,832 | 7 |
| prompt_injections | 339 | 440 | 856 | 238 | 27,613 | 0 |
| pubmedqa | 354 | 499 | 1051 | 525 | 262,438 | 0 |
| rewardbench2 | 630 | 1532 | 4252 | 1886 | 2,262,656 | 1 |
| scienceqa_text | 356 | 550 | 884 | 194 | 194,026 | 0 |
| scifact_rank_choice | 1736 | 10627 | 13655 | 3169 | 950,821 | 0 |
| scifact_rank_noul | 2916 | 6263 | 7599 | 6014 | 1,804,128 | 0 |
| sst5 | 372 | 670 | 1637 | 208 | 103,769 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** nfcorpus_rank_choice: 4. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-cloudflare-clef-flash-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

