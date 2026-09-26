# Benchmarks for Jev and related decision models

Checked 25 September 2026. These are published measurements, not runs performed in this workspace. [Model details](01_models_and_architecture.md) · [training](03_training_platforms_and_usage.md).

**Recommended starting suite:** independent Typed Decisions for distributions, JevBench for diverse decisions and operating costs, a few established labeled datasets for independent ground truth, and a private holdout from your intended workflow. No single public leaderboard establishes production reliability.

## Which benchmark comes from whom?

| Benchmark | Contents and provenance | What it does not establish |
|---|---|---|
| **TypeSafe Workflow Evals** | Vendor's four workflows: security incidents, agent traces, invoices, customer service. Fixed code combines model judgments. References average GPT-6 Astra and Claude Fable 5.1 at high thinking; evaluated models use provider defaults. | Human-verified correctness, unbiased task selection, or equal reasoning budgets. Workflow outcome is not identical to per-question accuracy. |
| **LocalLLaMA/typed-decisions** | Independent synthetic suite: 1,200 training cases and 400 test cases, five decisions each; 6,000 train / 2,000 test decisions. Four workflow families. Soft gold averages three teacher samples at temperature 0.7. | Real customer prevalence or human ground truth. Teacher agreement is the target; the reported ~73.5% self-agreement is an empirical reference, not a mathematical ceiling. |
| **JevBench, fstandhartinger** | Independent harness spanning routing, answer judging, policy checks, intent, ordinal scores, and enum extraction; native and verbalized probabilities are distinguished. Public and private items. | Full local reproduction of sealed items, universal cost estimates, or a version-independent composite score. |
| **Harry Munro's Jev–Laya benchmark** | 1,470 synthetic items, eight tasks; committed questions, labels, predictions, and timing. Laya runs through MLX on an M3 Pro; Jev uses its API. | A hardware-controlled model comparison or broad real-world ground truth. |

Sources: [TypeSafe evaluation methodology](https://evals.typesafe.ai/), [Typed Decisions card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), [JevBench](https://github.com/fstandhartinger/jevbench), [paired Jev–Laya study](https://github.com/harrymunro/jev-laya-benchmark).

For Typed Decisions, send only `state` and `questions`; retain `gold` for scoring. Never expose its latent `factors` to the model. Separate zero-shot generalists from models fitted on these workflows. Distribution agreement with a fallible teacher is useful, but cannot settle real-world calibration. [Dataset schema and construction](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)

## A shared benchmark with Gemma-based results

The archived **JevBench v1.3.0 scoring report** uses 534 decisions and appears in the repository's historically named `RESULTS-v1.2.md`. These are tier accuracies, not the composite leaderboard score:

| Implementation | Easy | Standard | Judge | Hard |
|---|---:|---:|---:|---:|
| Jev 1.13.0 | 100.0% | 99.0% | 94.5% | **74.1%** |
| djev, Maisa's DiffusionGemma service | 100.0% | 97.9% | 93.2% | **69.5%** |
| OpenJev, razorback16's DiffusionGemma implementation | 100.0% | 95.8% | 91.1% | **65.5%** |
| Laya 421M English base | 94.4% | 72.9% | 69.2% | **34.1%** |

Laya used CPU execution and its 512-token input budget; truncation affects the hard tier. Some self-hosted latency figures were artificially adjusted to approximate production load, and some costs use proxy tariffs. Use raw measurements for your own economics. [Results and implementation footnotes](https://github.com/fstandhartinger/jevbench/blob/main/RESULTS-v1.2.md)

The live README now describes **v1.4.1**, adding 308 sealed decisions and changing aggregation to a harmonic mean with additional penalties. Therefore, archive the commit, item hashes, adapter, and scoring version; do not compare its composite numbers with v1.3.0. Public-only runs are partial reproductions. [Current methodology](https://github.com/fstandhartinger/jevbench)

The paired synthetic Jev–Laya study reports **92.9% versus 65.3%** over 3,386 judgments. Its speed result is workload-dependent: one-question p50 was 136 ms for Jev versus 42 ms locally for Laya; at 50 questions on one state, 170 ms versus 1,002 ms. That is evidence for testing question batching, not a universal speed multiplier. [Recorded measurements](https://github.com/harrymunro/jev-laya-benchmark)

## Established datasets to add

| Dataset / original source | What to test | Important omission or adaptation |
|---|---|---|
| [BANKING77, PolyAI](https://github.com/PolyAI-LDN/task-specific-datasets) | Fine-grained intent: 77 banking classes, 10,003 train and 3,080 test examples | Fixed domain; no natural probability labels. Test all 77 options separately from a shortlist experiment. |
| [BoolQ, Google Research](https://github.com/google-research-datasets/boolean-questions) | Passage-grounded binary decisions; 15,942 naturally occurring questions overall | Binary answers do not test multi-option or ordinal behavior. Keep passage and question intact. |
| [MASSIVE, Amazon](https://huggingface.co/datasets/AmazonScience/massive) | Multilingual intent; 51 languages, 60 intents, roughly one million utterances | Slot filling is a different task. A 20-option sampled test is not the full 60-intent task. |
| [XNLI, original repository](https://github.com/facebookresearch/XNLI) | Entailment / contradiction / neutral across 15 languages; 7,500 evaluation pairs per language | Translation and NLI coverage do not establish operational routing quality. |

For an ordinal slice, the [Laya evaluation notebook](https://github.com/NandhaKishorM/laya/blob/main/research/scripts/laya_benchmark_colab.ipynb) supplies SST-5 sentiment evaluation, plus emotion and prompt-injection tasks. Report ordinal error as well as exact accuracy. Its small injection subset is a diagnostic, not a security certification.

Some familiar datasets occur in the training mixtures of these models. Laya reports AG News and BoolQ in its mixture; Together trains on MultiNLI, BoolQ, Banking77, AG News, and SST-5. Held-out records from an exposed task measure in-domain generalization, not unseen-task transfer. [Laya benchmark report](https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md), [Together data mixture](https://www.together.ai/blog/how-to-train-your-own-jev)

## Metrics to collect

These are my recommended measurement choices:

| Question | Metric |
|---|---|
| Are labels correct, including rare classes? | Accuracy, macro-F1, per-class precision/recall, confusion matrix |
| Are probabilities useful? | Negative log-likelihood, Brier score, reliability plots; ECE with stated binning |
| Does a model match soft references? | KL divergence from reference to prediction, total variation; declare clipping and Brier normalization |
| Are ordinal errors small? | MAE and ranked probability score; state whether levels have equal spacing |
| Can software safely abstain? | Risk–coverage curve; error at fixed coverage and coverage at a chosen error target |
| Is the workflow successful? | Final action accuracy and an explicit cost matrix for incorrect actions/escalations |
| Does it fit the service budget? | End-to-end p50/p95/p99, failures, throughput, cost per 1,000 decisions |

For hard labels, use `Brier = mean_i sum_k (p_ik - y_ik)^2`. If averaging over classes too, label that convention. Record true-label zero probabilities instead of hiding them through numerical clipping. Low ECE alone can reward an uninformative base-rate predictor.

## A concrete first evaluation

1. **Freeze a private test before training.** Start with approximately 1,000 independently labeled cases covering your workflows, ambiguous cases, rare costly errors, and negative controls. This is a proposed pilot size, not a guarantee of enough statistical power. Separate train, calibration, and test by customer/document/template or time.
2. **Run two tracks.** Generalist: unseen schemas, no domain fitting. Specialist: identical allowed training data and a separate calibration split. Include base Laya, tuned Laya, Jev, Tev, a selected djev runtime, and a simple classifier baseline where applicable.
3. **Preserve the decision task.** Same state, criteria, options, and score scale. Log truncation, label encoding, prompt templates, precision, model revision, temperature files, and sampler settings. Missing outputs count as failures.
4. **Stress the interface.** Permute option order; swap opaque option names without changing meanings; test negation, irrelevant context, missing evidence, contradictory facts, and instruction-like text inside state. Sweep 2/10/50/77 options and short/long inputs.
5. **Measure serving realistically.** Sweep 1/5/20/50 questions per state and concurrency separately. Record cold and warm runs. Measure from your intended client region, including Singapore if that is the deployment location.
6. **Report uncertainty.** Bootstrap by case, not by individual question when several share a state. Publish paired differences and confidence intervals. Tune routing thresholds only on calibration data, then freeze them for the test.

TypeSafe explicitly documents trouble with numerical precision, indirection, irrelevant context, and adversarial content; these belong in the stress set. [Jev 1.13 known limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)

**What is still missing:** a common, independently adjudicated, untouched test that compares all requested implementations under matched training access and serving conditions. The available results are useful preliminary evidence, not a single winner ranking.
