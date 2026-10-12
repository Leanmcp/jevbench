# jev-bench results: or-cloudflare-clef-omni-full

Scored 2026-10-11T19:52:53-0700. Model requested `or-cloudflare-clef-omni`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8480** | [0.816, 0.880] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7900** | [0.754, 0.826] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.6740** | [0.634, 0.718] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.9480** | [0.928, 0.966] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.1024** | [1.026, 1.182] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9250** | [0.897, 0.950] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.8571** | [0.750, 0.946] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **0.9231** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4675** | [0.391, 0.538] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7250** | [0.688, 0.763] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.7950** | [0.761, 0.828] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.7150** | [0.676, 0.751] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 96.6% | **0.3573** | [0.324, 0.393] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3797** | [0.346, 0.416] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3612** | [0.325, 0.396] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.7155** | [0.629, 0.793] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.6740** | [0.632, 0.716] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.5600** | [0.522, 0.594] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9210** | [0.899, 0.942] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7233** | [0.682, 0.768] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7162** | [0.669, 0.760] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5233** | [0.487, 0.559] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 94.8% | 0.9458 | 0.1272 | 0.4028 | 0 | 0.1887 | 1000 |
| mcpbench_server_routing | 112 | 28 | 85.7% | 0.8347 | 0.2392 | 0.6420 | 0 | 0.2088 | 112 |
| mcpbench_tool_selection | 26 | 13 | 92.3% | 0.8974 | 0.1568 | 0.3941 | 0 | 0.2766 | 26 |
| mcpmark_server_routing | 338 | 8 | 46.7% | 0.4883 | 0.6945 | 1.4538 | 0 | 0.1896 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0167 | 0.1093 | 0 | 0.1024 | 18 |
| medmcqa | 1000 | 4 | 72.5% | 0.7252 | 0.3757 | 0.7253 | 0 | 0.0332 | 1000 |
| medqa_usmle | 1000 | 4 | 79.5% | 0.7951 | 0.2940 | 0.5774 | 0 | 0.0479 | 1000 |
| mmlu_pro | 1000 | 10 | 71.5% | 0.7117 | 0.3944 | 0.9462 | 0 | 0.0712 | 1000 |
| pubmedqa | 500 | 3 | 67.4% | 0.5542 | 0.4888 | 0.8908 | 0 | 0.1761 | 500 |
| rewardbench2 | 1200 | 4 | 56.0% | 0.5605 | 0.5909 | 1.1273 | 0 | 0.0701 | 1200 |
| scienceqa_text | 1000 | 4 | 92.1% | 0.9291 | 0.1091 | 0.1974 | 0 | 0.0465 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 84.8% | 15.2% | 86.4% | 16.8% | 0.9082 | 0.1232 | 0.0755 | 50.0% |
| aegis2_response | 500 | 79.0% | 21.0% | 76.0% | 18.0% | 0.8850 | 0.1496 | 0.0808 | 50.0% |
| atbench500 | 500 | 67.4% | 32.6% | 36.0% | 1.2% | 0.8990 | 0.2253 | 0.1636 | 50.0% |
| jailbreak_classification | 400 | 92.5% | 7.5% | 91.5% | 6.9% | 0.9803 | 0.0517 | 0.0358 | 35.2% |
| prompt_injections | 116 | 71.6% | 28.4% | 45.0% | 0.0% | 0.9872 | 0.1829 | 0.1564 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 25.8% | 72.2% | 1.102 | 0.2048 | 0.444 |
| nfcorpus_rank_graded | 4924 | 3 | 64.6% | 94.6% | 0.443 | 0.1470 | 0.490 |
| sst5 | 500 | 5 | 57.6% | 97.2% | 0.523 | 0.0827 | 0.880 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 288 | 0.3573 | 0.5967 | 0.1632 | 0.3295 | 0.4673 | 18.8% |
| nfcorpus_rank_graded | 298 | 0.3797 | 0.6291 | 0.1747 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3612 | 0.5983 | 0.1713 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7233 | 0.7075 | 0.8017 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7162 | 0.6946 | 0.8159 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 47.5% |
| rewardbench2 | Focus | 240 | 64.2% |
| rewardbench2 | Math | 240 | 61.7% |
| rewardbench2 | Precise IF | 240 | 25.0% |
| rewardbench2 | Safety | 240 | 81.7% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 94.8% | 94.8% | 94.8% | 0.0% |
| mcpbench_server_routing | 56 | 85.7% | 85.7% | 85.7% | 0.0% |
| mcpbench_tool_selection | 4 | 92.3% | 92.3% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 46.7% | 46.7% | 46.7% | 0.0% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 72.2% | 72.8% | 69.0% | 7.0% |
| medqa_usmle | 500 | 79.2% | 79.8% | 76.4% | 6.2% |
| mmlu_pro | 500 | 71.4% | 71.6% | 65.6% | 11.8% |
| rewardbench2 | 594 | 55.2% | 56.8% | 48.8% | 14.5% |
| scienceqa_text | 500 | 92.4% | 91.8% | 89.4% | 5.4% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 355 | 6285 | 6766 | 246 | 122,848 | 0 |
| aegis2_response | 297 | 624 | 1544 | 348 | 173,787 | 0 |
| atbench500 | 351 | 612 | 1281 | 1960 | 979,844 | 0 |
| banking77 | 377 | 5662 | 5755 | 1843 | 1,843,104 | 7 |
| helpsteer2_helpfulness | 335 | 5327 | 6045 | 750 | 375,028 | 0 |
| jailbreak_classification | 276 | 383 | 1007 | 459 | 183,654 | 0 |
| mcpbench_server_routing | 269 | 816 | 1141 | 994 | 111,348 | 0 |
| mcpbench_tool_selection | 270 | 324 | 813 | 832 | 21,630 | 0 |
| mcpmark_server_routing | 261 | 504 | 1030 | 322 | 108,790 | 0 |
| mcpmark_tool_selection | 291 | 364 | 364 | 466 | 8,394 | 0 |
| medmcqa | 313 | 472 | 1277 | 206 | 206,378 | 16 |
| medqa_usmle | 279 | 35259 | 35329 | 371 | 371,456 | 100 |
| mmlu_pro | 296 | 408 | 1017 | 406 | 406,402 | 299 |
| nfcorpus_rank_choice | 552 | 4910 | 5554 | 2608 | 751,045 | 0 |
| nfcorpus_rank_graded | 307 | 730 | 1724 | 372 | 1,831,200 | 593 |
| nfcorpus_rank_noul | 586 | 1450 | 1866 | 4753 | 1,416,496 | 65 |
| prompt_injections | 283 | 428 | 1280 | 238 | 27,550 | 57 |
| pubmedqa | 292 | 451 | 991 | 523 | 261,459 | 305 |
| rewardbench2 | 330 | 902 | 2029 | 1887 | 2,264,110 | 204 |
| scienceqa_text | 269 | 405 | 641 | 191 | 191,122 | 669 |
| scifact_rank_choice | 351 | 481 | 864 | 3178 | 953,489 | 48 |
| scifact_rank_noul | 447 | 736 | 1166 | 6004 | 1,801,065 | 52 |
| sst5 | 269 | 402 | 1244 | 205 | 102,313 | 281 |

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

Artifacts: `data/runs/or-cloudflare-clef-omni-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

