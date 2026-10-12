# jev-bench results: liquid-d1-full

Scored 2026-10-11T18:57:40-0700. Model requested `liquid-d1`, endpoint `https://api.liquid.ai/decisions/v1/systemone`, manifest pinned 2026-09-26. One typed question per request, except `*_rank_noul` slices, which ask one noul per candidate document in a single request.

## Headline

| slice | type | cases | coverage | value | 95% CI | metric |
|---|---|---|---|---|---|---|
| aegis2 | noul | 500 | 100.0% | **0.8660** | [0.834, 0.894] | accuracy |
| aegis2_response | noul | 500 | 100.0% | **0.7880** | [0.752, 0.820] | accuracy |
| atbench500 | noul | 500 | 100.0% | **0.7860** | [0.748, 0.820] | accuracy |
| banking77 | choice | 1000 | 100.0% | **0.8570** | [0.828, 0.884] | accuracy |
| jailbreak_classification | noul | 400 | 100.0% | **0.9650** | [0.945, 0.983] | accuracy |
| mcpbench_server_routing | choice | 112 | 100.0% | **0.9018** | [0.821, 0.964] | server_routing_accuracy |
| mcpbench_tool_selection | choice | 26 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| mcpmark_server_routing | choice | 338 | 100.0% | **0.4586** | [0.388, 0.533] | server_routing_accuracy |
| mcpmark_tool_selection | choice | 18 | 100.0% | **1.0000** | n/a | tool_selection_accuracy |
| medmcqa | choice | 1000 | 100.0% | **0.7700** | [0.736, 0.803] | accuracy |
| medqa_usmle | choice | 1000 | 100.0% | **0.8660** | [0.837, 0.892] | accuracy |
| mmlu_pro | choice | 1000 | 100.0% | **0.6640** | [0.627, 0.701] | accuracy |
| prompt_injections | noul | 116 | 100.0% | **0.7155** | [0.629, 0.802] | accuracy |
| pubmedqa | choice | 500 | 100.0% | **0.7040** | [0.660, 0.742] | accuracy |
| scienceqa_text | choice | 1000 | 100.0% | **0.9580** | [0.942, 0.973] | accuracy |
| sst5 | score | 500 | 100.0% | **0.5080** | [0.472, 0.544] | mae_expected_level |

Confidence intervals are percentile bootstrap over 2000 resamples grouped by `family_id`, so a case and its reordered twin move together. Accuracy is higher-is-better; MAE is lower-is-better. The two are not comparable to each other.

## Choice slices

| slice | n | gold classes | accuracy | macro-F1 | Brier | NLL | zero-prob on gold | ECE (10 bins) | n with probs |
|---|---|---|---|---|---|---|---|---|---|
| banking77 | 1000 | 77 | 85.7% | 0.8478 | 0.2002 | 0.4927 | 0 | 0.0320 | 1000 |
| mcpbench_server_routing | 112 | 28 | 90.2% | 0.8865 | 0.1345 | 0.2465 | 0 | 0.0667 | 112 |
| mcpbench_tool_selection | 26 | 13 | 100.0% | 1.0000 | 0.0001 | 0.0032 | 0 | 0.0032 | 26 |
| mcpmark_server_routing | 338 | 8 | 45.9% | 0.3704 | 0.7382 | 1.7814 | 0 | 0.2163 | 338 |
| mcpmark_tool_selection | 18 | 5 | 100.0% | 1.0000 | 0.0000 | 0.0003 | 0 | 0.0003 | 18 |
| medmcqa | 1000 | 4 | 77.0% | 0.7697 | 0.3315 | 0.6745 | 0 | 0.0831 | 1000 |
| medqa_usmle | 1000 | 4 | 86.6% | 0.8659 | 0.1905 | 0.3413 | 0 | 0.0574 | 1000 |
| mmlu_pro | 1000 | 10 | 66.4% | 0.6595 | 0.4597 | 1.0956 | 0 | 0.1105 | 1000 |
| pubmedqa | 500 | 3 | 70.4% | 0.5572 | 0.4604 | 1.0263 | 0 | 0.1739 | 500 |
| scienceqa_text | 1000 | 4 | 95.8% | 0.9685 | 0.0621 | 0.1080 | 0 | 0.0201 | 1000 |

Brier is the sum convention, `mean_i sum_k (p_ik - y_ik)^2`. NLL excludes cases where the gold option got exactly zero mass; that count is its own column rather than being clipped away. ECE over 10 equal-width bins on the top probability: the bin count changes the number, so it travels with it.

## Binary slices

| slice | n | acc @0.5 | acc if flipped | positive recall | FPR | AUROC | Brier | ECE | base rate |
|---|---|---|---|---|---|---|---|---|---|
| aegis2 | 500 | 86.6% | 13.4% | 84.0% | 10.8% | 0.9398 | 0.0985 | 0.0308 | 50.0% |
| aegis2_response | 500 | 78.8% | 21.2% | 75.2% | 17.6% | 0.8857 | 0.1405 | 0.0293 | 50.0% |
| atbench500 | 500 | 78.6% | 21.4% | 58.8% | 1.6% | 0.9650 | 0.1371 | 0.0723 | 50.0% |
| jailbreak_classification | 400 | 96.5% | 3.5% | 90.1% | 0.0% | 0.9941 | 0.0334 | 0.0321 | 35.2% |
| prompt_injections | 116 | 71.6% | 28.4% | 45.0% | 0.0% | 0.9890 | 0.2429 | 0.2495 | 51.7% |

`acc if flipped` is a diagnostic for label polarity, not evidence that labels should be reversed. Higher flipped accuracy can reflect model errors, threshold effects, or a small sample. For slices with unverified label semantics in `common.POLARITY_ASSUMPTIONS`, verify the source mapping independently before drawing conclusions; never choose polarity to improve a model's score. AUROC measures ranking without a fixed threshold, but does not establish calibration or resolve label semantics.

## Ordinal slices

| slice | n | levels | exact (rounded) | within 1 level | MAE (expected level) | RPS | Spearman |
|---|---|---|---|---|---|---|---|
| sst5 | 500 | 5 | 57.2% | 98.0% | 0.508 | 0.0803 | 0.878 |

The score type returns an expected zero-based level index, so MAE is computed on that expected value and exact accuracy on its rounding. Levels are treated as equally spaced, which SST-5 does not actually guarantee.

## Option-order sensitivity

| slice | families with both | original order | permuted order | both correct | flipped by reordering |
|---|---|---|---|---|---|
| banking77 | 500 | 84.6% | 86.8% | 82.4% | 6.6% |
| mcpbench_server_routing | 56 | 91.1% | 89.3% | 87.5% | 5.4% |
| mcpbench_tool_selection | 4 | 100.0% | 100.0% | 100.0% | 0.0% |
| mcpmark_server_routing | 169 | 44.4% | 47.3% | 41.4% | 8.9% |
| mcpmark_tool_selection | 3 | 100.0% | 100.0% | 100.0% | 0.0% |
| medmcqa | 500 | 78.8% | 75.2% | 71.8% | 10.4% |
| medqa_usmle | 500 | 86.6% | 86.6% | 83.6% | 6.0% |
| mmlu_pro | 500 | 67.4% | 65.4% | 59.6% | 13.6% |
| scienceqa_text | 500 | 96.2% | 95.4% | 94.0% | 3.6% |

`flipped by reordering` is the fraction of matched families where moving the options changed whether the answer was right. Reordering does not change the question, so anything materially above zero is position bias, not difficulty.

## Runtime

| slice | p50 ms | p95 ms | p99 ms | mean input tokens | total input tokens | retries |
|---|---|---|---|---|---|---|
| aegis2 | 413 | 1132 | 1802 | 195 | 97,588 | 78 |
| aegis2_response | 410 | 625 | 1342 | 300 | 150,182 | 146 |
| atbench500 | 1756 | 2493 | 3002 | 1929 | 964,500 | 0 |
| banking77 | 1986 | 2571 | 3170 | 511 | 511,410 | 0 |
| jailbreak_classification | 455 | 833 | 1194 | 412 | 164,927 | 96 |
| mcpbench_server_routing | 223 | 388 | 476 | 539 | 60,398 | 159 |
| mcpbench_tool_selection | 238 | 533 | 558 | 583 | 15,148 | 20 |
| mcpmark_server_routing | 219 | 567 | 1908 | 184 | 62,276 | 271 |
| mcpmark_tool_selection | 232 | 1186 | 1186 | 366 | 6,584 | 8 |
| medmcqa | 378 | 691 | 1252 | 126 | 125,623 | 261 |
| medqa_usmle | 407 | 1278 | 3209 | 284 | 284,206 | 257 |
| mmlu_pro | 402 | 794 | 1232 | 248 | 247,800 | 346 |
| prompt_injections | 399 | 1219 | 2362 | 182 | 21,167 | 46 |
| pubmedqa | 433 | 850 | 1293 | 450 | 225,084 | 178 |
| scienceqa_text | 395 | 1067 | 2833 | 134 | 133,717 | 346 |
| sst5 | 389 | 529 | 1105 | 117 | 58,646 | 203 |

Measured end to end from this client at concurrency 1, which is a property of this machine and network as much as of the model. Token counts are the API's own `usage`, not an estimate.

## What these numbers do not establish

- **MCP scope.** These are offline derived slices, not official MCPMark or MCP-Bench end-to-end scores. Server routing is separate from function selection. Tool selection uses a small authored subset of hypothetical checkpoints and curated candidate catalogues; no tool execution or argument correctness is measured. Public-task training exposure is unknown. Pinned sources: `mcp_sources.json`; labels: `annotations/mcp_tools.json`.
- **MCP coverage.** Headlines use valid returned decisions. `scores.json` also reports accuracy over planned cases, counting errors and missing predictions as wrong. Multiple checkpoints from one task share the bootstrap family; small subsets do not support broad ranking claims.
- **Truncated states.** atbench500: 34, jailbreak_classification: 1. Those cases were not shown the full record, so the slice is not a faithful full-input evaluation.
- **Training exposure.** banking77 (reported), medqa_usmle (likely), mmlu_pro (likely), scienceqa_text (likely), sst5 (reported). Held-out rows from a task a model was trained on measure in-domain generalisation, not transfer. Do not average across this flag.
- **One question per request.** Latency here is per single decision. Jev's published advantage grows when many questions share one state, and that configuration is not measured here.
- **`best_threshold_accuracy` in scores.json is optimistic** by construction: it is chosen on the same data it scores. Pick operating thresholds on a calibration split before quoting one.
- **Vendor-adjacent framing.** Instructions and criteria here are ours. A different wording is a different benchmark, which is why the exact adapter is in the repo.
- **SST-5 text is not redistributable** under an unspecified upstream license. The predictions file carries no state text, so it can be published as is.

Artifacts: `data/runs/liquid-d1-full/predictions.jsonl`, `scores.json`, `meta.json`, cases in `data/cases/`, pinned sources in `sources.json`.

