# jev-bench results: jev-1.13.0-20260926T133639

Scored 2026-10-11T19:01:53-0700. Model requested `jev-1.13.0`, endpoint `https://api.typesafe.ai/v1/systemone`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8280** | [0.794, 0.862] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.8120** | [0.778, 0.848] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.9300** | [0.908, 0.952] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8130** | [0.780, 0.845] | accuracy |
| helpsteer2_helpfulness | score | 500 | 100.0% | **0.9598** | [0.896, 1.031] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9750** | [0.960, 0.988] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9554** | [0.902, 0.991] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.5148** | [0.441, 0.592] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7810** | [0.745, 0.815] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8730** | [0.844, 0.900] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.8060** | [0.773, 0.838] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 100.0% | **0.3611** | [0.328, 0.398] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3768** | [0.343, 0.414] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3782** | [0.344, 0.416] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.7328** | [0.647, 0.810] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.7060** | [0.666, 0.746] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.7925** | [0.764, 0.823] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9570** | [0.939, 0.972] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.7386** | [0.697, 0.784] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.7505** | [0.709, 0.793] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5071** | [0.464, 0.551] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 81.3% | 0.7918 | 0.2940 | 0.4146 | 59 | 0.0811 | 1000 |
| mcpbench_server_routing | 112 | 28 | 95.5% | 0.9528 | 0.0864 | 0.1796 | 0 | 0.0772 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0001 | 0.0027 | 0 | 0.0027 | 26 |
| mcpmark_server_routing | 338 | 8 | 51.5% | 0.4336 | 0.6886 | 1.2268 | 29 | 0.2081 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0007 | 0.0063 | 0 | 0.0061 | 18 |
| medmcqa | 1000 | 4 | 78.1% | 0.7807 | 0.2987 | 0.5348 | 8 | 0.0442 | 1000 |
| medqa_usmle | 1000 | 4 | 87.3% | 0.8723 | 0.1770 | 0.3017 | 4 | 0.0228 | 1000 |
| mmlu_pro | 1000 | 10 | 80.6% | 0.8053 | 0.2872 | 0.5637 | 17 | 0.0587 | 1000 |
| pubmedqa | 500 | 3 | 70.6% | 0.6114 | 0.4652 | 0.6918 | 27 | 0.1900 | 500 |
| rewardbench2 | 1200 | 4 | 79.2% | 0.7920 | 0.2826 | 0.5422 | 0 | 0.0445 | 1200 |
| scienceqa_text | 1000 | 4 | 95.7% | 0.9697 | 0.0615 | 0.0955 | 0 | 0.0106 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 82.8% | 17.2% | 76.8% | 11.2% | 0.9225 | 0.1187 | 0.0288 | 50.0% |
| aegis2_response | 500 | 81.2% | 18.8% | 72.0% | 9.6% | 0.9089 | 0.1337 | 0.0255 | 50.0% |
| atbench500 | 500 | 93.0% | 7.0% | 86.8% | 0.8% | 0.9927 | 0.0748 | 0.1386 | 50.0% |
| jailbreak_classification | 400 | 97.5% | 2.5% | 92.9% | 0.0% | 0.9979 | 0.0217 | 0.0304 | 35.2% |
| prompt_injections | 116 | 73.3% | 26.7% | 48.3% | 0.0% | 0.9784 | 0.1881 | 0.1621 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 33.2% | 79.6% | 0.960 | 0.1721 | 0.482 |
| nfcorpus_rank_graded | 4924 | 3 | 58.3% | 94.4% | 0.499 | 0.1799 | 0.484 |
| sst5 | 500 | 5 | 58.8% | 95.4% | 0.507 | 0.0912 | 0.861 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 298 | 0.3611 | 0.6215 | 0.1638 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_graded | 298 | 0.3768 | 0.6256 | 0.1724 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3782 | 0.6247 | 0.1740 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.7386 | 0.7276 | 0.8073 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.7505 | 0.7357 | 0.8259 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 81.2% |
| rewardbench2 | Focus | 240 | 92.1% |
| rewardbench2 | Math | 240 | 78.8% |
| rewardbench2 | Precise IF | 240 | 46.2% |
| rewardbench2 | Safety | 240 | 97.9% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 81.6% | 81.0% | 80.0% | 2.6% |
| mcpbench_server_routing | 56 | 92.9% | 98.2% | 92.9% | 5.4% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 50.3% | 52.7% | 47.3% | 8.3% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 78.4% | 77.8% | 75.4% | 5.4% |
| medqa_usmle | 500 | 87.0% | 87.6% | 85.4% | 3.8% |
| mmlu_pro | 500 | 81.2% | 80.0% | 78.0% | 5.2% |
| rewardbench2 | 594 | 78.5% | 80.0% | 74.1% | 10.3% |
| scienceqa_text | 500 | 95.6% | 95.8% | 94.0% | 3.4% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 806 | 1227 | 1815 | 418 | 209,106 | 0 |
| aegis2_response | 781 | 842 | 927 | 525 | 262,552 | 0 |
| atbench500 | 807 | 1170 | 2241 | 2253 | 1,126,628 | 0 |
| banking77 | 780 | 871 | 1196 | 1702 | 1,702,138 | 0 |
| helpsteer2_helpfulness | 135 | 214 | 394 | 890 | 444,877 | 0 |
| jailbreak_classification | 766 | 915 | 2095 | 634 | 253,628 | 0 |
| mcpbench_server_routing | 133 | 243 | 490 | 1077 | 120,608 | 0 |
| mcpbench_tool_selection | 6228 | 6273 | 6278 | 1018 | 26,462 | 0 |
| mcpmark_server_routing | 158 | 6255 | 6274 | 488 | 165,100 | 0 |
| mcpmark_tool_selection | 149 | 173 | 173 | 650 | 11,694 | 0 |
| medmcqa | 766 | 3757 | 11780 | 386 | 386,012 | 1 |
| medqa_usmle | 780 | 5728 | 19768 | 555 | 554,644 | 0 |
| mmlu_pro | 791 | 5769 | 11818 | 568 | 568,206 | 0 |
| nfcorpus_rank_choice | 140 | 195 | 235 | 2750 | 819,608 | 0 |
| nfcorpus_rank_graded | 134 | 193 | 422 | 553 | 2,721,713 | 0 |
| nfcorpus_rank_noul | 163 | 223 | 296 | 4678 | 1,393,954 | 0 |
| prompt_injections | 771 | 5720 | 19780 | 408 | 47,370 | 0 |
| pubmedqa | 790 | 7758 | 19817 | 731 | 365,287 | 0 |
| rewardbench2 | 147 | 249 | 559 | 2052 | 2,462,144 | 0 |
| scienceqa_text | 790 | 5795 | 19795 | 378 | 378,308 | 0 |
| scifact_rank_choice | 152 | 223 | 544 | 3445 | 1,033,449 | 0 |
| scifact_rank_noul | 176 | 518 | 966 | 5911 | 1,773,244 | 0 |
| sst5 | 803 | 5796 | 11787 | 345 | 172,578 | 0 |

Measured end to end from this client at concurrency 4, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/jev-1.13.0-20260926T133639/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

