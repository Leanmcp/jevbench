# Jev, Laya, and DiffusionGemma: preliminary research

Checked 25 September 2026. Primary documentation, model cards, benchmark artifacts, and training code were inspected directly. No models or training jobs were run. Companion files: [benchmarks](02_benchmarks_and_evaluation.md), [training and use](03_training_platforms_and_usage.md).

**The main finding:** these products share a decision interface, but they do not share one disclosed architecture or training algorithm. Jev's size remains undisclosed; Laya is an inspectable encoder-based model; the Gemma examples apply structured inference to an existing Google model; Together's implementation uses supervised fine-tuning.

## Identity and parameter counts

| System | Parameters | Architecture / implementation | Access |
|---|---|---|---|
| **TypeSafe AI Jev**, current documented `jev-1.13.0` | **Not publicly disclosed in the sources inspected** | Proprietary architecture, parallel sampler, RLCD post-training; exact backbone and layer configuration unreported | Hosted API; no customer weight fine-tuning |
| **Convai Innovations Laya** | **421.3M**: 394.8M encoder + 26.5M head | ModernBERT-large plus decision head | Open weights and code |
| **Laya multilingual** | **321.9M**: 306.9M encoder + 15.0M head | mmBERT-base plus decision head | Open weights and code |
| **Laya typed-decisions** | About **421M** | Domain-adapted ModernBERT-large variant | Open specialist checkpoint |
| **Google DiffusionGemma-26B-A4B-it** | Card lists **25.2B total, 3.8B active**, and separately lists a **~550M vision encoder**; marketed as 26B/A4B | Gemma 4 sparse MoE with discrete diffusion | Apache-2.0 weights; community decision servers |
| **Together Tev1-4B-experimental** | **4B base-model class** | Qwen3.5-4B with LoRA SFT and existing output head | Published weights, hosted endpoint, training recipe |

Sources: [Jev model documentation](https://docs.typesafe.ai/models), [Laya benchmark notebook parameter breakdown](https://github.com/NandhaKishorM/laya/blob/main/research/scripts/laya_benchmark_colab.ipynb), [Laya model card](https://huggingface.co/convaiinnovations/laya), [Google model card](https://huggingface.co/google/diffusiongemma-26B-A4B-it), [Tev repository](https://github.com/togethercomputer/tev1).

## What is architecturally different?

**Jev:** TypeSafe's launch announcement identifies three changes: architecture, parallel sampling, and **Reinforcement Learning for Calibrated Decisions (RLCD)**. It does not disclose enough to establish whether its backbone is a conventional transformer, diffusion model, or another design. Neither low price nor latency determines parameter count. There is no defensible public layer-by-layer reconstruction in these sources. The announced applications include routing, scoring, verification, guardrails, and workflow branching. [TypeSafe launch, 15 September](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

**Laya:** a bidirectional transformer encoder feeds a head containing two transformer layers, option-marker scoring, and an act/escalate component. Options are represented at marked positions and normalized within each question, allowing callers to supply new rubrics. The encoder is fine-tuned too. This is recognizably a neural classifier architecture; its distinguishing features are the schema-conditioned head and probability-oriented training. The English checkpoint's default context is 512 tokens, versus 1,024 for the specialist. [Architecture and checkpoint details](https://huggingface.co/convaiinnovations/laya)

The multilingual checkpoint defaults to 1,024 tokens but supports an explicit `max_len=8192`. The project reports variable quality beyond roughly 4,000 tokens; accepting a longer input does not establish reliable long-context decisions. [Multilingual checkpoint](https://huggingface.co/convaiinnovations/laya-multilingual)

**DiffusionGemma:** transformer attention and diffusion are not competing categories: attention describes the network; diffusion describes training/decoding behavior. Google's design uses causal prompt prefill and bidirectional canvas denoising, with 30 layers and 8 active experts out of 128 plus a shared expert. The card gives a 256K context ceiling. Those base-model specifications do not establish the usable context or accuracy of a particular decision server. [Google model card](https://huggingface.co/google/diffusiongemma-26B-A4B-it)

The likely “Gemma Jev” reference is **community structured-read software**, such as [mmastrac/djev](https://github.com/mmastrac/djev) and its [Cloud Run adaptation](https://github.com/taeold/djev-run). Another implementation is Maisa's djev service, measured in JevBench. These should not be collapsed into one release. I found no official Google model named “Gemma Jev,” nor evidence that these wrappers reproduce TypeSafe's RLCD.

**Tev:** the specific Qwen3.5-4B backbone is a hybrid: 32 layers arranged in eight groups of three Gated DeltaNet blocks followed by one gated-attention block, with feed-forward layers. It is not simply a small all-attention decoder. Tev keeps that backbone and trains a short answer-letter output using LoRA. The client's JSON result is assembled around that letter. [Qwen's specific 4B configuration](https://huggingface.co/Qwen/Qwen3.5-4B), [Tev training guide](https://github.com/togethercomputer/tev1/blob/main/docs/TRAINING.md)

## Training: what is known

| System | Documented training | What remains unestablished |
|---|---|---|
| Jev | RLCD aims at calibrated decisions; common weights across accounts | Base model, parameter count, corpus, reward formula, optimizer, compute budget, reproducible training implementation |
| Laya | Public implementation uses probability-scoring rewards and noisy-logit policy gradients; its current specialist notebook also includes soft cross-entropy | It is an independent implementation, not evidence of Jev's internal algorithm |
| DiffusionGemma decision wrappers | Reuse Google weights and change inference | A wrapper-specific RLCD training stage or calibration guarantee |
| Tev | LoRA supervised fine-tuning on 37,840 training examples; 4,568 development examples | Exact historical job settings are not fully verified in the retained run record |

Sources: [TypeSafe RLCD description](https://docs.typesafe.ai/introduction/machine-learning-primer), [Laya training code](https://github.com/NandhaKishorM/laya/blob/main/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb), [djev structured reads](https://github.com/mmastrac/djev), [Tev run record](https://github.com/togethercomputer/tev1/blob/main/runs/new-v1/README.md).

## Accuracy worth quoting, with its scope

| Result | Reported measurement | Interpretation |
|---|---|---|
| Jev 1.13.0 on independent Typed Decisions | **72.7%**, 2,000 decisions; Brier **0.148**, ECE **0.144** | Zero-shot agreement with synthetic teacher labels |
| Laya typed-decisions on that test set | **76.6%**; Brier **0.062**, ECE **0.213** | Fine-tuned on the suite's training workflows; not a zero-shot win over Jev |
| Base Laya / multilingual on that suite | **36.2% / 35.2%** | Specialization matters substantially |
| Tev development evaluation | **880/1,000 correct**; policy-transfer **300/300** | Reused development sets, not untouched final tests |
| DiffusionGemma base model | MMLU-Pro **77.6%**, GPQA Diamond **73.2%** | Google's normal instruction-model evaluation; not structured-read decision accuracy |

Sources: [independent Typed Decisions dataset](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), [Laya reported results](https://github.com/NandhaKishorM/laya), [Tev saved evaluation](https://github.com/togethercomputer/tev1/blob/main/runs/new-v1/README.md), [Google benchmark table](https://huggingface.co/google/diffusiongemma-26B-A4B-it).

There is no single comparable “accuracy” across these rows. The benchmark file adds a shared JevBench comparison, data provenance, and a recommended evaluation plan.

## Practical selection

My recommendation is to use **Jev as a hosted reference**, **Laya for small-model training experiments**, **Tev for the easiest documented managed fine-tuning path**, and **DiffusionGemma structured reads for an inference-focused experiment**. A proper-scoring-rule objective encourages good probabilities; it does not prove calibration on unseen customer data. Compare an RL-based recipe against ordinary soft-label cross-entropy and held-out temperature scaling before attributing an improvement to RLCD.
