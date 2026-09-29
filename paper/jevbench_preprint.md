# Typed Decisions Under Audit: A Cross-Implementation Benchmark of Compact Decision Models

**Draft preprint, 26 September 2026.** Author list, affiliations and acknowledgements to be completed. All numbers reported here were produced by the runs described in Section 4 and are reproducible from the released artifacts.

---

## Abstract

A class of compact models has emerged that does not generate text but emits typed decisions: a probability for a yes/no question, a distribution over named options, or an expected level on an ordered rubric. These models are marketed on latency and calibration rather than on reasoning, and they are evaluated almost entirely by their own vendors. We construct jev-bench, a 12-slice benchmark spanning binary, multi-option and ordinal decisions over medicine, examination, banking intent, sentiment and agent safety, and evaluate three independent implementations of the typed-decision interface on identical inputs: a hosted commercial model (Jev 1.13), an open reimplementation on a diffusion backbone (djev-0.1 on DiffusionGemma 26B-A4B, served on one A100 80GB), and a 421M-parameter local model (Laya). We collect 24,818 decisions with full probability vectors.

Three findings hold across the suite. First, all three models are materially miscalibrated at the natural operating point: moving the decision threshold alone raises accuracy from 73.3% to 94.8% for the commercial model on prompt-injection detection, and from 64.7% to 83.6% for the open reimplementation, with optimal thresholds as low as 0.002. Reported accuracy at a 0.5 threshold therefore understates every model we tested. Second, sensitivity to option order differs by an order of magnitude between implementations, from 2.6-5.4% of matched items flipping under reordering for the commercial model to 12.0-33.6% for the other two, which places a floor on how finely multi-option results can be interpreted. Third, the 421M model is statistically indistinguishable from random guessing on four of six multi-option slices while simultaneously outperforming both larger models on prompt-injection detection at the default threshold, indicating that the typed-decision interface admits models with sharply non-overlapping competence rather than a single quality ordering.

We additionally report the first evaluation we are aware of for the image path of an open typed-decision model, and show by controlled ablation that its accuracy on image-grounded multiple choice (82.8%) is close to its accuracy on the text-only rows of the same dataset (84.7%). We release the case set, the adapters, and all 24,818 predictions with their complete probability vectors.

---

## 1 Introduction

Most evaluation of language models assumes a generative interface. A model is prompted, it produces tokens, and the tokens are parsed. A different interface has become commercially significant: the model is given a state and a typed question, and returns a decision directly, reading the probabilities of the allowed labels rather than generating and reparsing prose. Three question types cover the products we examined: a single probability for a yes/no question, a distribution over named options, and an expected index over an ordered rubric.

This interface is worth evaluating separately for three reasons. The output is a distribution rather than a string, so calibration is a first-class property rather than an afterthought. The latency profile is different, since there is no autoregressive decode. And the deployment pattern is different: these models sit in front of other systems as routers, guards and classifiers, where a miscalibrated probability produces an unsafe action rather than an unsatisfying paragraph.

Public evidence about these models comes predominantly from their vendors or from single-implementation harnesses. Vendor evaluations use reference answers derived from consensus among larger models rather than independent ground truth, and they do not hold reasoning budgets equal across compared systems. Independent harnesses exist but have covered one implementation at a time, with sealed items that cannot be locally reproduced.

We make four contributions.

1. **A cross-implementation benchmark.** 12 slices, 8,016 text cases, built from eight public datasets pinned to exact commit hashes, with a single adapter per question type so that three independently developed implementations receive byte-identical inputs.
2. **A measurement of the operating-point problem.** We show that the 0.5 threshold, which is the natural reading of a probability and the one every default integration uses, is wrong for all three models, and we quantify the accuracy left on the table.
3. **A measurement of interface fragility.** By constructing a reordered twin of every multi-option case, we separate positional preference from task competence, and find that it differs by an order of magnitude across implementations.
4. **Released predictions, not just scores.** All 24,818 decisions with full probability vectors, so that calibration, risk-coverage and distributional agreement can be recomputed by others without re-running any model.

Our aim is diagnostic rather than competitive. We do not claim to rank these systems for production use, and Section 7 sets out why the results should not be read that way.

---

## 2 What a typed decision is

The research literature has no settled name for the interface this paper evaluates, so we define it before measuring it. Readers familiar with classification heads, constrained decoding or reranking will recognise pieces of each; Section 3 says where the differences lie.

### 2.1 The interface, informally

A caller supplies a **state**, which is any text or JSON describing a situation, together with one or more **typed questions**. Each question declares its answer space up front. The model returns a distribution over exactly that declared space and nothing else. It emits no prose, and there is nothing to parse.

Three question types cover every product we examined. The examples below are real requests from our suite with the probabilities the commercial model actually returned.

**Noul, a yes/no probability.** An agent trajectory is supplied as state, and the question asks whether the agent behaved unsafely. The answer is one number, 0.90, which the application compares against a threshold of its own choosing. Nothing in the protocol says what that threshold should be, which turns out to matter a great deal (Section 6.2).

**Choice, a distribution over named options.** A medical examination question is supplied as state, with four options declared as criteria. The returned distribution was `{a: 0.01, b: 0.00, c: 0.99, d: 0.00}` and the correct option was `c`. The caller receives the full vector, not just the argmax, which is what makes calibration measurable at all.

**Score, an expected level on an ordered rubric.** A sentence is supplied as state and the rubric is declared as an ordered list, here `["very negative", "negative", "neutral", "positive", "very positive"]`. The model returned level probabilities (0.99, 0.01, 0, 0, 0) and the answer 0.01, which is the *expected* level index, not the most likely one. The distinction is not cosmetic: a distribution (0.2, 0.5, 0.3) yields an expected level of 1.1 while its mode is 1, so evaluation code that rounds the expected value and evaluation code that takes the mode are measuring different quantities.

A single request may carry many questions against one state, and the vendors' latency claims are strongest in that regime. We deliberately send one question per request throughout, for the reasons in Section 8.

### 2.2 The interface, formally

Let `s` be a state and `q` a question with type `τ(q) ∈ {noul, choice, score}` and a caller-declared, ordered label set `L_q = (l_1, ..., l_K)`. A typed-decision model defines a conditional distribution supported on that declared set:

> `p_θ(· | s, q) ∈ Δ^{K-1}`, where `Δ^{K-1} = { p ∈ R^K_{≥0} : Σ_j p_j = 1 }`

The three types differ only in how a decision is read from `p_θ`:

| type | read | note |
|---|---|---|
| noul, K=2 | `π = p_θ(true | s,q)`, decision `d_γ(π) = 1[π ≥ γ]` | not a decision until a threshold γ is supplied from outside the model |
| choice | `ĵ = argmax_j p_j` | full vector also returned |
| score, levels 0..K-1 | `E[Y] = Σ_k k·p_k ∈ [0, K-1]` | the expected level, not the mode |

The convention `γ = 0.5` is an assumption of the integrator, not a property of the model, and Section 6.2 shows it is the wrong assumption for every system we tested.

**Label-restricted reading.** The implementations we study do not sample a string and parse it. Let `z = f_θ(s,q) ∈ R^|V|` be the logits at a designated answer position over vocabulary `V`, and let `t_j ∈ V` identify label `l_j`. The returned distribution is the softmax restricted and renormalised over the declared labels alone:

> `p_j = exp(z_{t_j}) / Σ_{k=1..K} exp(z_{t_k})`

Two consequences are worth stating because both are measurable. Every declared label receives positive mass by construction, so a faithful implementation cannot assign zero probability to the correct option; Section 6.5 reports one implementation achieving exactly that across 4,500 multi-option cases and another failing it on more than a third of a 77-option slice. And the cost is one forward pass regardless of K, rather than one pass per candidate token.

**Calibration.** A model is calibrated if its numbers mean what they say: for all `v ∈ [0,1]` and all labels `l`,

> `Pr(Y = l | p_θ(l | s,q) = v) = v`

Calibration is distinct from **discrimination**, which concerns only the ranking that `p_θ` induces and is measured threshold-free by AUROC. The distinction is the backbone of Section 6.2, where we exhibit a model with AUROC 0.978 and accuracy 73.3% at γ = 0.5: its ordering is nearly perfect while its absolute values are displaced downward.

**Order invariance.** For a permutation σ of `{1..K}`, write `σq` for the question with its labels reordered. Reordering options does not change what was asked, so a model that reads the question rather than the layout should satisfy

> `p_θ(l_{σ(j)} | s, σq) = p_θ(l_j | s, q)` for all j

We measure the **flip rate**: the fraction of matched pairs `(q, σq)` whose correctness differs. It bounds how much of a reported accuracy is attributable to label position rather than to the task. One caution: a model at chance accuracy has a high expected flip rate mechanically, so the flip rate is interpretable only alongside an accuracy above chance.

**Confidence is not a probability of correctness.** These implementations also return a scalar derived from the concentration of `p`, for instance `1 - H(p)/log K` with `H` the Shannon entropy. It is a property of the output distribution and carries no calibration guarantee. We never use it as a correctness estimate, and report AUROC and expected calibration error instead.

## 3 Related work

*Citations in this section are placeholders to be completed and verified against primary sources before submission. No reference below should be included without checking the exact venue, year and author list. This draft deliberately does not fabricate bibliography entries.*

**Vendor and independent evaluation of typed-decision models.** The commercial vendor publishes a four-workflow evaluation covering security incidents, agent traces, invoice processing and customer service, with reference answers derived from agreement among larger models. Independent harnesses have evaluated the same interface with public and sealed items, and a separate paired study has compared the commercial model against a small local model on synthetic items. We describe how our design differs in Section 3.

**Calibration.** We report Brier score under the sum convention, negative log-likelihood, expected calibration error with a declared bin count, and the ranked probability score for ordinal slices. The known weaknesses of expected calibration error, in particular its sensitivity to binning and its tolerance of uninformative base-rate predictors, apply here and we report accompanying metrics for that reason.

**Option-order sensitivity in multiple-choice evaluation.** Sensitivity of model answers to the order and labelling of options is documented for generative models. We measure the analogous property for a model that returns a probability over named options rather than emitting a letter.

**Agent and content safety benchmarks.** Four of our slices derive from published safety corpora for agent trajectories, content moderation, prompt injection and jailbreak classification.

---

## 4 Benchmark construction

### 3.1 Sources

Eight public datasets, each pinned to a commit hash on the Hugging Face Hub and recorded with its licence and an exposure flag. Row counts were measured from the downloaded files rather than taken from dataset cards.

| Slice | Source | Licence | Type | Options | Exposure |
|---|---|---|---|---|---|
| medmcqa | openlifescienceai/medmcqa | apache-2.0 | choice | 4 | unknown |
| medqa_usmle | GBaker/MedQA-USMLE-4-options | cc-by-4.0 | choice | 4 | likely |
| mmlu_pro | TIGER-Lab/MMLU-Pro | mit | choice | 4-10 | likely |
| banking77 | mteb/banking77 | mit (data CC-BY-4.0, PolyAI) | choice | 77 | reported |
| pubmedqa | qiaojin/PubMedQA | mit | choice | 3 | unknown |
| sst5 | SetFit/sst5 | unspecified | score | 5 levels | reported |
| scienceqa_text | derek-thomas/ScienceQA | cc-by-sa-4.0 | choice | 2-5 | likely |
| scienceqa_image | derek-thomas/ScienceQA | cc-by-sa-4.0 | choice | 2-5 | likely |
| vqa_rad | flaviagiammarino/vqa-rad | cc0-1.0 | noul | 2 | unknown |
| atbench500 | AI45Research/ATBench | apache-2.0 | noul | 2 | unknown |
| aegis2, aegis2_response | nvidia/Aegis-AI-Content-Safety-2.0 | cc-by-4.0 | noul | 2 | unknown |
| prompt_injections | deepset/prompt-injections | apache-2.0 | noul | 2 | unknown |
| jailbreak_classification | jackhhao/jailbreak-classification | apache-2.0 | noul | 2 | unknown |

**Exposure** records whether a dataset is reported in the training mixture of any evaluated model or its plausible base. BANKING77 and SST-5 appear in a published training recipe for this model family; MMLU-Pro, MedQA and ScienceQA are near-certain to appear in the pretraining of any large base model. Held-out rows from an exposed task measure in-domain generalisation, not transfer, and results must not be averaged across this flag.

### 3.2 Adapters and leakage control

Each source has an explicit allowlist of model-visible fields. The adapter constructs the state from the allowlist alone. Gold labels, rationales and risk annotations are stored outside the state and never sent. The fields excluded for this reason include the answer explanations in MedMCQA, MMLU-Pro, PubMedQA and ScienceQA, the risk-source, failure-mode and real-world-harm annotations in ATBench, and the violated-category taxonomy in Aegis.

A verification pass checks, for every built case, that gold is reachable among the presented options, that request limits are respected, and that no hidden field appears in the state. The reverse-direction check produced 33 flags on ScienceQA which we investigated and found to be false positives: the dataset's `solution` field quotes the question stem verbatim before reasoning, and its `lecture` field is duplicated into the visible `hint` upstream. We report this because the naive check has its causality backwards, and a benchmark that treats such flags as leaks will discard valid cases.

### 3.3 Sampling and perturbation

Cases are sampled deterministically under a fixed seed, stratified proportionally with a floor of one per observed class so that a 500-family sample of BANKING77 retains all 77 intents. For every multi-option slice we construct a **reordered twin**: the same question with the same options presented in a shuffled order, so the correct option moves position. Both variants share a family identifier and are resampled together in the bootstrap. This yields 8,016 text cases from 5,516 families.

### 3.4 Protocol

One typed question per request, so one decision per case. This simplifies scoring and makes per-decision latency comparable across slices. It also forgoes the batching regime in which this model class is reported to be fastest, which we note as a limitation rather than mixing it in as a variable.

States are capped at 12,000 characters and every truncated case is flagged. 34 ATBench cases and one jailbreak case were truncated by this cap.

---

## 5 Experimental setup

| System | Description | Serving |
|---|---|---|
| Jev 1.13.0 | Hosted commercial typed-decision model | Vendor HTTP API, client in Singapore |
| djev-0.1 | Open typed-decision layer over DiffusionGemma 26B-A4B via vLLM, pinned at source revision `3ce907e`, one denoising step | One NVIDIA A100-SXM4-80GB, driver 580.178.04, `max_model_len` 8192, `gpu_memory_utilization` 0.85, BF16 weights and KV cache, seed 0, samples 1 |
| Laya 421M (English) | Local non-autoregressive decision model | Apple M3 Pro, MPS, 512-token default context |

Identical case files were sent to all three. djev requests pinned `seed=0` and `samples=1`; the hosted API exposes no equivalent control, which we note in Section 7. Predictions record the decision, the full probability vector, latency, token usage and error state, but never the state text, which keeps the released predictions publishable for sources whose text cannot be redistributed.

**Cost and duration.** The djev text suite completed 8,016 cases in 19.4 minutes with zero errors at concurrency 6, consuming 51 minutes of A100 time in total including model startup. The hosted API consumed 6.03M input tokens. The Laya suite ran on a laptop.

---

## 6 Results

### 5.1 Main comparison

Accuracy with 95% percentile bootstrap intervals over 2,000 resamples grouped by family. SST-5 reports mean absolute error on the expected level, where lower is better. "Chance" is the mean per-case random-guess rate, which accounts for the varying option counts in MMLU-Pro and ScienceQA.

| Slice | n | Chance | Laya 421M | djev-0.1 | Jev 1.13 |
|---|---:|---:|---:|---:|---:|
| jailbreak_classification | 400 | 35.2% | 93.0 [90.3, 95.5] | 96.5 [94.5, 98.3] | **97.5** [96.0, 98.8] |
| scienceqa_text | 1000 | 43.4% | 53.4 [50.0, 56.9] | 84.7 [82.0, 87.3] | **95.7** [93.9, 97.2] |
| atbench500 | 500 | 50.0% | 65.4 [61.0, 69.4] | 75.8 [71.8, 79.6] | **93.0** [90.8, 95.2] |
| medqa_usmle | 1000 | 25.0% | 26.1 [22.9, 29.4] | 71.2 [67.5, 74.8] | **87.3** [84.4, 90.0] |
| aegis2 | 500 | 50.0% | 54.2 [49.6, 58.8] | 81.0 [77.4, 84.2] | **82.8** [79.4, 86.2] |
| banking77 | 1000 | 1.3% | 36.3 [32.6, 40.1] | 71.4 [67.8, 75.0] | **81.3** [78.0, 84.5] |
| aegis2_response | 500 | 50.0% | 52.8 [48.6, 57.2] | 69.2 [65.2, 73.0] | **81.2** [77.8, 84.8] |
| mmlu_pro | 1000 | 11.1% | 12.5 [10.2, 15.1] | 42.3 [38.5, 45.9] | **80.6** [77.3, 83.8] |
| medmcqa | 1000 | 25.0% | 26.9 [23.6, 30.4] | 53.8 [50.1, 57.4] | **78.1** [74.5, 81.5] |
| prompt_injections | 116 | 51.7% | **81.0** [73.3, 87.9] | 64.7 [56.0, 73.3] | 73.3 [64.7, 81.0] |
| pubmedqa | 500 | 33.3% | 32.8 [28.8, 37.2] | 62.2 [58.2, 66.4] | **70.6** [66.6, 74.6] |
| sst5 (MAE, lower better) | 500 | n/a | 0.849 [0.796, 0.905] | 0.544 [0.501, 0.588] | **0.507** [0.464, 0.551] |

The ordering Laya < djev < Jev holds on 11 of 12 slices. That three independently developed implementations order consistently across binary, multi-option and ordinal tasks is evidence that the harness measures a coherent capability rather than an artefact of our prompt wording.

**The exception is informative.** On prompt-injection detection the 421M model outperforms both larger systems at the default threshold, by 7.7 points over the commercial model. Section 5.2 shows this is a threshold effect rather than superior discrimination, but the effect is real for any integration that uses 0.5.

**Four slices are at chance for the 421M model.** MedMCQA 26.9 against 25.0, MedQA 26.1 against 25.0, MMLU-Pro 12.5 against 11.1, and PubMedQA 32.8 against 33.3, which is below chance. The same model reaches 93.0% on jailbreak classification. Competence within this interface is therefore not a single scalar.

### 5.2 The operating point is wrong for every model

For binary slices we report accuracy at the conventional 0.5 threshold, the threshold that maximises accuracy on the same data, and the area under the ROC curve, which is threshold-free.

| Slice | Model | Acc @0.5 | Best threshold | Acc at best | AUROC | ECE |
|---|---|---:|---:|---:|---:|---:|
| prompt_injections | Jev | 73.3 | 0.07 | **94.8** | 0.978 | 0.162 |
| prompt_injections | djev | 64.7 | 0.002 | **83.6** | 0.880 | 0.333 |
| prompt_injections | Laya | 81.0 | 0.253 | 85.3 | 0.922 | 0.056 |
| aegis2_response | djev | 69.2 | 0.005 | **81.0** | 0.879 | 0.267 |
| atbench500 | Jev | 93.0 | 0.33 | 97.0 | 0.993 | 0.139 |
| atbench500 | djev | 75.8 | 0.147 | 80.6 | 0.855 | 0.190 |
| aegis2 | djev | 81.0 | 0.007 | 84.2 | 0.914 | 0.168 |
| jailbreak | Laya | 93.0 | 0.963 | 99.5 | 0.998 | 0.012 |

Accuracy at the best threshold is selected on the data it scores and is therefore optimistic; it is reported as a diagnostic of available headroom, not as an operating point.

Two observations follow. **The commercial model's worst slice is not a capability failure.** Its AUROC on prompt injection is 0.978, meaning it separates the classes almost perfectly, while its accuracy at 0.5 is 73.3% because its probabilities sit below the threshold. **The open reimplementation is more severely affected**, with optimal thresholds between 0.002 and 0.147 and expected calibration error up to 0.333. Laya shows the opposite sign on jailbreak classification, with an optimal threshold of 0.963.

The direction and magnitude of the offset differ by implementation and by slice, so there is no single correction. The practical consequence is that any comparison of these systems at a fixed 0.5 threshold measures probability placement as much as decision quality, and every accuracy figure in Section 5.1 understates the model that produced it.

### 5.3 Option-order sensitivity

Fraction of matched families whose correctness changed when the options were reordered. Reordering does not change the question, so any value materially above zero is positional preference.

| Slice | Jev 1.13 | djev-0.1 | Laya 421M |
|---|---:|---:|---:|
| banking77 | 2.6% | 12.0% | 16.2% |
| medqa_usmle | 3.8% | 14.4% | 20.6% |
| scienceqa_text | 3.4% | 15.4% | 33.6% |
| mmlu_pro | 5.2% | 20.6% | 13.0% |
| medmcqa | 5.4% | 26.4% | 21.8% |

An order of magnitude separates the commercial model from the other two. For djev and Laya this places a floor on interpretation: differences of a few points between multi-option slices are within the noise introduced by option placement alone.

For Laya the mechanism is direct. On MedMCQA it selected the first option 431 times out of 1,000 while the gold answer was in first position 267 times, and on MMLU-Pro it selected the first option 247 times against a gold frequency of 100. The commercial model's selections tracked the gold distribution closely (274/272/236/218 against 267/260/248/225). A model whose accuracy is near chance and whose answers are order-driven is not performing the task.

### 5.4 Context budget is a confound that must be measured, not assumed

The same 500 ATBench trajectories, as reported by each serving stack:

| Model | Mean input tokens | Accuracy |
|---|---:|---:|
| Laya 421M | **512** | 65.4% |
| djev-0.1 | 1,988 | 75.8% |
| Jev 1.13 | 2,253 | 93.0% |

Laya's figure is exactly its context limit on every case, meaning the trajectories were internally truncated. Our own truncation flag did not catch this, because it tracks only the harness's 12,000-character cap. Part of Laya's deficit on this slice is therefore a budget difference rather than a capability difference, and we do not attempt to attribute the split. djev at 8192 tokens saw substantially complete inputs, so its 17-point gap to the commercial model on the same slice is not explained by truncation.

Benchmarks comparing models with different context budgets should report per-case input tokens as measured by each serving stack. Tokenizer differences alone do not account for gaps of this size: on MedMCQA the same cases were 79 tokens for Laya against 386 for the commercial model.

### 5.5 Probability mass on the gold option

Count of cases where the correct option received exactly zero probability.

| Slice | Jev 1.13 | djev-0.1 | Laya 421M |
|---|---:|---:|---:|
| banking77 (77 options) | 59 | **0** | 349 |
| pubmedqa | 27 | **0** | 0 |
| mmlu_pro | 17 | **0** | 0 |
| medmcqa | 8 | **0** | 0 |

djev assigned non-zero mass to the correct option in every one of 4,500 multi-option cases, including all 1,000 at 77 options. This is consistent with its documented mechanism of reading the probabilities of the allowed label tokens directly rather than relying on the answer appearing in a truncated top-k list. Laya failed this on more than a third of BANKING77 cases. Any evaluation relying on log-likelihood of the gold option must report this count rather than clipping it away, since a single zero makes the average infinite.

### 5.6 Image-grounded decisions

We evaluated the image path of the open implementation. Neither of the other systems could be evaluated here: the commercial API route available to us has no image input, and the 421M model is text-only.

| Slice | n | Accuracy | Notes |
|---|---:|---:|---|
| scienceqa_image | 500 | 82.8 [79.6, 86.2] | macro-F1 0.825, ECE 0.086 |
| scienceqa_text | 1000 | 84.7 [82.0, 87.3] | same dataset, same adapter, rows without images |
| vqa_rad | 251 | 78.1 [72.9, 83.3] | base rate 47%, AUROC 0.884 |

The ScienceQA pair is a controlled comparison: identical model, identical adapter code, identical dataset, differing only in whether the answer requires the image. The 1.9-point difference has overlapping intervals.

**Verification that the image is consumed.** Sending 12 VQA-RAD cases twice, identical except for the image, every pair increased input tokens by 254 to 274 with no exceptions, and 3 of 12 decisions changed. With the image removed the model answered "no" to all 12 cases, producing varied answers only when the image was present. Accuracy with the image on that small sample was lower than without (66.7% against 75.0%), but the no-image condition is a degenerate always-negative predictor and 9 of the 12 golds were negative; we report it to forestall the misreading.

**Latency.** Image decisions cost 1,633ms (VQA-RAD) and 1,913ms (ScienceQA) at the median against 781ms for text on the same hardware.

---

## 7 Discussion

**Calibration, not accuracy, is the binding constraint.** The largest single improvement available to any model in this study is not a better model but a better threshold: 21.5 points for the commercial model on prompt injection, 18.9 for the open reimplementation on Aegis responses. Since these systems are deployed as gates whose threshold determines an action, this is an operational finding, not a scoring technicality. Threshold selection belongs on a calibration split, and vendors should publish a recommended operating point rather than leaving integrators to assume 0.5.

**The interface admits non-overlapping competence.** A 421M model at chance on four multi-option slices reached 93.0% on jailbreak classification with an AUROC of 0.998, and beat both larger systems on prompt injection at the default threshold. Buyers of this model class should evaluate on their own decision shape rather than on an aggregate score, and benchmark designers should resist reporting one.

**Reading a question and choosing among options is the discriminating capability.** The ordering across implementations is tightest on short binary safety decisions, where all three cluster between 93.0% and 97.5% on jailbreak classification, and widest on multi-option knowledge tasks, where the spread on MMLU-Pro is 12.5 to 80.6. Option-order sensitivity follows the same pattern.

---

## 8 Limitations

1. **Prompt wording is ours.** Instructions and criteria were written by us, not by any vendor. A different phrasing is a different benchmark. We release the exact adapters so this is inspectable rather than assumed.
2. **One question per request.** This model class is reported to be fastest when many questions share one state. That regime is not measured here, so our latency figures should not be read as the best these systems can do.
3. **Serving conditions are not matched.** The commercial model is remote, the open implementation is on a local A100 behind an SSH tunnel, and the 421M model is on a laptop. Latency comparisons are system comparisons.
4. **Sampling controls are not matched.** djev requests pinned seed and sample count; the hosted API exposes no equivalent, so its variance is unmeasured and single-run.
5. **Training exposure.** Five slices are flagged `reported` or `likely`. Results must not be averaged across that flag.
6. **Truncation.** 34 ATBench and 1 jailbreak case exceeded the harness cap. Separately, Laya internally truncated every ATBench case to 512 tokens, which our flag did not detect.
7. **Balanced slices do not estimate deployment incident rates.** A prevalence-matched evaluation is required for that claim and is not included.
8. **Best-threshold accuracy is optimistic**, chosen on the data it scores.
9. **Label polarity is assumed for two sources** whose cards do not state it. We report accuracy under both polarities; in every case the assumed direction was the higher one.
10. **Single run per model.** No seed variation is reported for the hosted model, and the open implementation was run at a single fixed seed.
11. **prompt_injections has only 116 cases**, giving intervals roughly 8 points wide. Conclusions drawn from it, including the threshold finding, are correspondingly weaker than those from the 1,000-case slices.

---

## 9 Reproducibility and artifacts

Released: the pinned source manifest with commit hashes, licences and exposure flags; the download and verification scripts; the adapters; all built cases; and 24,818 predictions with full probability vectors, latency and token usage. Also released is the serving provenance for the open implementation: the exact vLLM command line, the container log, the pinned source revision and the live capability configuration.

Predictions carry no source text, keyed instead by case identifier, which allows them to be published for sources whose text cannot be redistributed. Licences do not merge across sources: each is released with its own licence field, and SST-5, whose card states no licence, is distributed as identifiers and content hashes rather than text.

---

## 10 Use of AI assistance

This work used an AI coding assistant for harness implementation, data inspection and drafting of this manuscript. All experimental results were produced by the released code. Numerical claims were read from the released artifacts rather than transcribed. The authors are responsible for all content and have verified the claims against the artifacts. This disclosure is provided in line with ACL policy on AI writing assistance; the exact wording should be adapted to the target venue's current requirements before submission.

---

## Appendix A: To complete before submission

- Author list, affiliations, funding and conflicts of interest, including any relationship to the evaluated vendors.
- Verify and complete every reference in Section 2. No bibliography entry in this draft has been checked against a primary source.
- Confirm redistribution terms for each source against its current licence.
- Add a paired bootstrap on shared case identifiers for the model-versus-model claims. Section 5.1 reports unpaired intervals.
- Consider adding: the multi-sample deliberation baseline, the 421M model's typed-decisions checkpoint at 1,024 tokens, and MMLU-Pro restricted to four options to separate option starvation from capability.
