# jev-bench results: or-upstage-solar-decide-full

Scored 2026-10-11T19:42:07-0700. Model requested `or-upstage-solar-decide`, endpoint `https://openrouter.ai/api/alpha/decisions`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8080** | [0.774, 0.842] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7540** | [0.718, 0.792] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7380** | [0.698, 0.776] | accuracy |
| banking77 | choice | 114 | 0.0% | no usable records | n/a | n/a |
| helpsteer2_helpfulness | score | 500 | 100.0% | **1.0720** | [0.987, 1.160] | mae_expected_level |
| jailbreak_classification | noul | 400 | 100.0% | **0.9650** | [0.945, 0.983] | accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4793** | [0.411, 0.553] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **0.9444** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7220** | [0.686, 0.755] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8310** | [0.802, 0.860] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.7250** | [0.689, 0.761] | accuracy |
| nfcorpus_rank_choice | rank | 298 | 96.6% | **0.3045** | [0.272, 0.338] | ndcg@10 |
| nfcorpus_rank_graded | score | 4924 | 100.0% | **0.3543** | [0.321, 0.391] | ndcg@10 |
| nfcorpus_rank_noul | rank | 298 | 100.0% | **0.3240** | [0.289, 0.359] | ndcg@10 |
| prompt_injections | noul | 116 | 100.0% | **0.7069** | [0.621, 0.784] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.5940** | [0.550, 0.636] | accuracy |
| rewardbench2 | choice | 1200 | 100.0% | **0.7500** | [0.719, 0.778] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9620** | [0.948, 0.975] | accuracy |
| scifact_rank_choice | rank | 300 | 100.0% | **0.6301** | [0.583, 0.678] | ndcg@10 |
| scifact_rank_noul | rank | 300 | 100.0% | **0.5567** | [0.504, 0.610] | ndcg@10 |
| sst5 | score | 500 | 100.0% | **0.5990** | [0.538, 0.660] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0048 | 0.0313 | 0 | 0.0296 | 26 |
| mcpmark_server_routing | 338 | 8 | 47.9% | 0.4088 | 0.9278 | 3.2882 | 2 | 0.4250 | 338 |
| mcpmark_tool_selection | 18 | 5 | 94.4% | 0.9492 | 0.1020 | 0.2191 | 0 | 0.0358 | 18 |
| medmcqa | 1000 | 4 | 72.2% | 0.7221 | 0.4600 | 1.2844 | 0 | 0.1936 | 1000 |
| medqa_usmle | 1000 | 4 | 83.1% | 0.8313 | 0.2735 | 0.6023 | 0 | 0.1022 | 1000 |
| mmlu_pro | 1000 | 10 | 72.5% | 0.7266 | 0.4277 | 1.2941 | 1 | 0.1498 | 1000 |
| pubmedqa | 500 | 3 | 59.4% | 0.5748 | 0.7470 | 2.0725 | 0 | 0.3608 | 500 |
| rewardbench2 | 1200 | 4 | 75.0% | 0.7526 | 0.3782 | 0.9029 | 0 | 0.1214 | 1200 |
| scienceqa_text | 1000 | 4 | 96.2% | 0.9645 | 0.0635 | 0.1254 | 0 | 0.0094 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 80.8% | 19.2% | 67.2% | 5.6% | 0.8447 | 0.1666 | 0.1290 | 50.0% |
| aegis2_response | 500 | 75.4% | 24.6% | 55.2% | 4.4% | 0.8007 | 0.2021 | 0.1706 | 50.0% |
| atbench500 | 500 | 73.8% | 26.2% | 79.2% | 31.6% | 0.8011 | 0.1923 | 0.1390 | 50.0% |
| jailbreak_classification | 400 | 96.5% | 3.5% | 91.5% | 0.8% | 0.9495 | 0.0352 | 0.0191 | 35.2% |
| prompt_injections | 116 | 70.7% | 29.3% | 46.7% | 3.6% | 0.5851 | 0.2904 | 0.2642 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| helpsteer2_helpfulness | 500 | 5 | 32.6% | 70.8% | 1.072 | 0.2532 | 0.423 |
| nfcorpus_rank_graded | 4924 | 3 | 62.8% | 89.1% | 0.502 | 0.2291 | 0.404 |
| sst5 | 500 | 5 | 53.0% | 90.4% | 0.599 | 0.1385 | 0.806 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Ranking slices

| slice | queries | nDCG@10 | MRR@10 | Recall@10 | BM25 nDCG@10 | ceiling nDCG@10 | shortlist recall |
|---|---|---|---|---|---|---|---|
| nfcorpus_rank_choice | 288 | 0.3045 | 0.5603 | 0.1341 | 0.3295 | 0.4673 | 18.8% |
| nfcorpus_rank_graded | 298 | 0.3543 | 0.6001 | 0.1702 | 0.3319 | 0.4651 | 19.1% |
| nfcorpus_rank_noul | 298 | 0.3240 | 0.5180 | 0.1616 | 0.3319 | 0.4651 | 19.1% |
| scifact_rank_choice | 300 | 0.6301 | 0.6194 | 0.7197 | 0.6605 | 0.8300 | 82.6% |
| scifact_rank_noul | 300 | 0.5567 | 0.5437 | 0.6267 | 0.6605 | 0.8300 | 82.6% |

Each query reranks the same BM25 top-20 shortlist. `BM25 nDCG@10` is the shortlist's own order, so the model helps only where it beats that column. `ceiling nDCG@10` is the best possible order of the shortlist, and `shortlist recall` is the share of judged-relevant documents it contains; no reranker can exceed either. nDCG uses linear gain against every judged document for the query.

## By subset

| slice | subset | n | accuracy |
|---|---|---|---|
| rewardbench2 | Factuality | 240 | 64.2% |
| rewardbench2 | Focus | 240 | 94.6% |
| rewardbench2 | Math | 240 | 78.3% |
| rewardbench2 | Precise IF | 240 | 44.2% |
| rewardbench2 | Safety | 240 | 93.8% |

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 48.5% | 47.3% | 41.4% | 13.0% |
| mcpmark_tool_selection | 3 | 88.9% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 72.2% | 72.2% | 64.6% | 15.2% |
| medqa_usmle | 500 | 83.2% | 83.0% | 78.0% | 10.2% |
| mmlu_pro | 500 | 72.0% | 73.0% | 65.4% | 14.2% |
| rewardbench2 | 594 | 74.3% | 75.7% | 64.8% | 20.4% |
| scienceqa_text | 500 | 96.4% | 96.0% | 94.0% | 4.4% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 832 | 14916 | 19386 | 505 | 252,268 | 0 |
| aegis2_response | 633 | 15815 | 17801 | 607 | 303,429 | 0 |
| atbench500 | 7869 | 16261 | 18906 | 2223 | 1,111,555 | 0 |
| helpsteer2_helpfulness | 11283 | 19955 | 22113 | 934 | 467,105 | 0 |
| jailbreak_classification | 638 | 5906 | 16716 | 713 | 285,150 | 0 |
| mcpbench_tool_selection | 939 | 6360 | 8673 | 915 | 23,778 | 0 |
| mcpmark_server_routing | 10413 | 17797 | 18316 | 470 | 159,016 | 0 |
| mcpmark_tool_selection | 582 | 4044 | 4044 | 647 | 11,642 | 0 |
| medmcqa | 789 | 17032 | 20599 | 399 | 399,370 | 0 |
| medqa_usmle | 646 | 15886 | 17428 | 554 | 553,650 | 0 |
| mmlu_pro | 4439 | 16695 | 18851 | 545 | 544,710 | 0 |
| nfcorpus_rank_choice | 10892 | 18233 | 20540 | 2503 | 720,835 | 0 |
| nfcorpus_rank_graded | 2075 | 13342 | 16494 | 570 | 2,807,330 | 0 |
| nfcorpus_rank_noul | 12751 | 25054 | 30135 | 48457 | 14,440,038 | 0 |
| prompt_injections | 1601 | 15486 | 20707 | 497 | 57,662 | 0 |
| pubmedqa | 895 | 16201 | 19088 | 711 | 355,398 | 0 |
| rewardbench2 | 12406 | 16064 | 17608 | 1957 | 2,348,908 | 0 |
| scienceqa_text | 605 | 7884 | 15687 | 402 | 402,396 | 0 |
| scifact_rank_choice | 1427 | 18610 | 23746 | 2897 | 869,148 | 0 |
| scifact_rank_noul | 13122 | 22947 | 26821 | 61557 | 18,467,080 | 0 |
| sst5 | 650 | 13828 | 15148 | 390 | 194,814 | 0 |

Measured end to end from this client at concurrency 100, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **Failed requests.** banking77: 114, nfcorpus_rank_choice: 10. Coverage below 100% means the headline is computed on the cases that answered, which flatters a model that fails on hard inputs.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/or-upstage-solar-decide-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

