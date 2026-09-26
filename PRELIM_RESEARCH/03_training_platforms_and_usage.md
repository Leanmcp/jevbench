# Training, platforms, and practical use

Checked 25 September 2026. Commands below are **for you to execute**; no Python, Node, installers, model inference, or paid jobs were run. [Architectures](01_models_and_architecture.md) · [evaluation plan](02_benchmarks_and_evaluation.md).

**There is no verified turnkey public API for reproducing TypeSafe's proprietary RLCD in the sources checked.** There are public decision-training implementations, managed SFT, managed RL services, and custom GPU jobs. These are different levels of support.

## Platform support

| Platform / project | What is actually supported | Connection / work required |
|---|---|---|
| **TypeSafe** | Jev inference; no per-customer fine-tuning or LoRA | Console API key, bearer-authenticated `/v1/systemone`; adapt state and rubrics |
| **Laya on Kaggle** | Public two-T4 training notebook with RL-style reward optimization and auxiliary supervision | Import notebook, enable internet and `GPU T4 x2`; provide domain data; optional HF token for publishing |
| **Together managed fine-tuning** | Concrete Tev recipe using LoRA SFT | `TOGETHER_API_KEY`; upload train/dev files; create job; deploy output separately |
| **Together Custom Training** | RL beta advertises GRPO and custom losses, full-weight/LoRA | Request access. Confirm supported architecture and full-distribution gradient access before calling it suitable for Laya-style RLCD |
| **Hugging Face Jobs** | Arbitrary scripts/containers on GPU hardware | HF account, credits and job-authorized token; submit your trainer, persist checkpoints to Hub/storage |
| **Google Cloud custom training** | Custom containers and distributed worker pools | Project/IAM, GPU quota, Artifact Registry image, storage, `CustomJob`; you supply the objective |
| **Fireworks RFT** | Custom evaluators that score outputs and attach to reinforcement fine-tuning | Upload/validate evaluator and create RFT job; this does not establish native Jev or Laya support |
| **Cloud Run + djev-run** | A documented DiffusionGemma serving deployment | Google Cloud project, GPU capacity, weight storage and container; an inference route, not an RLCD training service |

Sources: [TypeSafe customization](https://docs.typesafe.ai/models), [Laya notebook](https://github.com/NandhaKishorM/laya/blob/main/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb), [Together recipe](https://github.com/togethercomputer/tev1/blob/main/examples/train_together.py), [Together RL beta](https://www.together.ai/custom-training), [HF Jobs](https://huggingface.co/docs/hub/jobs), [Google CustomJob](https://docs.cloud.google.com/vertex-ai/docs/training/create-custom-job), [Fireworks evaluators](https://docs.fireworks.ai/api-reference/create-evaluator), [djev-run](https://github.com/taeold/djev-run).

**Compatibility test for any managed RL platform:** can it train your exact backbone/head, expose probabilities over every allowed option, apply your distribution-level loss, and save that custom head? Rewarding a generated confidence string through an ordinary completion API is a different experiment. Generic “GRPO supported” does not answer these questions.

## 1. Use Jev as the hosted baseline

Create an API key in the [TypeSafe console](https://console.typesafe.ai/), place it in `TYPESAFE_API_KEY`, and use the documented HTTP interface. For reproducible measurements, use the versioned model name:

```bash
curl https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H 'Content-Type: application/json' \
  --data '{
    "model": "jev-1.13.0",
    "state": "The customer reports a duplicate charge and requests a refund.",
    "questions": {
      "refund_requested": {
        "type": "noul",
        "instructions": "Does the customer explicitly request a refund?"
      }
    }
  }'
```

Store the returned model ID, probabilities, token usage, timing, and errors. The API documents retryable rate-limit/overload responses. [HTTP request schema](https://docs.typesafe.ai/api)

Current documentation lists $0.042 per million input tokens, 64K total request tokens, and 32K for state plus the longest question. This is inference pricing, not training pricing. Jev's weights are shared across accounts; domain rules go into the request. [Model limits](https://docs.typesafe.ai/models)

## 2. Train Laya when you need an inspectable decision model

Laya describes rewards combining log and spherical scores, with ranked probability score for ordinal questions. Exploration perturbs logits with Gaussian noise; REINFORCE-style updates use a group-mean baseline. These are Laya's disclosed choices, not TypeSafe's unpublished recipe. [Training description](https://huggingface.co/convaiinnovations/laya)

Use the repository's [Kaggle fine-tuning notebook](https://github.com/NandhaKishorM/laya/blob/main/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb). Its current recipe updates encoder and head using four epochs, effective batch 64 across two T4s, encoder LR `2.5e-5`, head LR `1e-4`, four noisy-logit samples, and noise decreasing from 0.4 to 0.1. It combines a group-baseline policy-gradient loss with **1.0 × soft cross-entropy**. Thus, describing this notebook as pure RL would be inaccurate.

The notebook starts from 1,200 cases / 6,000 decisions, withholds calibration items before training, fits temperatures, and saves model/config/tokenizer artifacts under `/kaggle/working/laya_finetuned_typed_decisions`. Inspect that split carefully: it is formed at decision-item level; for your data, split by whole case to avoid shared-state leakage. These are code observations, not a reproduced training result. [Notebook implementation](https://github.com/NandhaKishorM/laya/blob/main/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb)

The README still describes calibration from training items and a roughly 30K-question, 4–5-hour run, conflicting with the current notebook. Pin a commit and inspect its data counts; do not budget from that runtime claim. [README fine-tuning section](https://github.com/NandhaKishorM/laya#fine-tuning)

For your own dataset, retain `state`, question instructions, candidate descriptions, and hard or soft targets. My recommended experiment is: identical initial weights and splits, compare cross-entropy alone against the combined objective, then calibrate each on the same held-out cases. Evaluate unseen schemas separately from familiar ones. Save calibration parameters with the checkpoint.

For a first local use test, the documented package supports:

```bash
python -m pip install 'laya[serve]'
LAYA_DEVICE=cuda LAYA_PRELOAD=1 laya-serve
```

Use the appropriate PyTorch build for your hardware. The server exposes `/v1/systemone`; set `LAYA_API_KEY` for bearer authentication when needed. The SDK supports explicit checkpoint selection:

```python
from laya import Router

router = Router()
result = router.predict(
    "A customer requests a refund for a duplicate payment.",
    {"refund": {"type": "noul", "instructions": "Is a refund requested?"}},
    model="english",
)
```

Use `model="typed-decisions"` when deliberately evaluating that specialist. [Router API](https://nandhakishorm.github.io/laya/reference/router/), [serving configuration](https://nandhakishorm.github.io/laya/docker/)

## 3. Train your own Tev-like model on Together

The September 23 article reports about **$17 and 25 minutes** for its example. That is a reported training-only experiment, not an all-in quote. Its prose inconsistently says 38,340 examples; the repository's validated final count is **37,840**. The mixture includes public classification data plus programmatic policy, routing, and taxonomy tasks. [Article](https://www.together.ai/blog/how-to-train-your-own-jev), [dataset record](https://github.com/togethercomputer/tev1/blob/main/docs/DATASET.md)

The proposed settings are LoRA rank 8, alpha 16, all-linear modules, one epoch, batch 8, LR `5e-5`, sequence length 2,048, and completion-only SFT. The repository explicitly says these are the saved starting recipe, not verified exact historical job settings. [Training script](https://github.com/togethercomputer/tev1/blob/main/examples/train_together.py)

Run these yourself in a fresh checkout; the project requires Python 3.12+ and `uv`:

```bash
git clone https://github.com/togethercomputer/tev1
cd tev1
uv sync --locked
cp .env.example .env
# Edit .env and set TOGETHER_API_KEY.
uv run python fetch_sources.py
uv run python build_all.py

# Preview first; the second command uploads data and starts billed training.
uv run --env-file .env python examples/train_together.py
uv run --env-file .env python examples/train_together.py --launch
```

For custom data, pass `--data path/to/instruction`. The directory contains `train.jsonl` and `dev.jsonl`; each record has a rendered `prompt` and answer-letter `completion` plus EOS. Preserve the selected tokenizer/chat template; do not template already-rendered prompts again. [Repository setup](https://github.com/togethercomputer/tev1), [input format](https://github.com/togethercomputer/tev1/blob/main/docs/TRAINING.md)

```bash
# Replace placeholders with values returned by your run.
uv run --env-file .env tg fine-tuning retrieve YOUR_JOB_ID --json

# After completion, use model_output_name from that response.
# Starts separately billed hosting; choose supported hardware in your account.
uv run --env-file .env tg endpoints create MODEL_OUTPUT_NAME \
  --hardware 1x_nvidia_h100_80gb_sxm --display-name my-decision-model --wait

# Set TOGETHER_MODEL in .env to the returned endpoint name.
uv run --env-file .env python examples/decide.py examples/charge-dispute.json

# Stop hosting when finished, using the endpoint ID.
uv run --env-file .env tg endpoints stop YOUR_ENDPOINT_ID
```

Do not rerun `--launch` to check status: it creates another job. [Official project workflow](https://github.com/togethercomputer/tev1/blob/main/docs/TRAINING.md)

For immediate use, the public checkpoint is [togethercomputer/Tev1-4B-experimental](https://huggingface.co/togethercomputer/Tev1-4B-experimental); the Together model ID is `together/Tev1-4B-experimental`, subject to account access. Use the supplied client settings: thinking disabled, temperature 0, short completion budget, constrained letters. Token log-probabilities still require independent calibration. [Tev usage and limitations](https://github.com/togethercomputer/tev1)

## 4. Use the DiffusionGemma decision implementations

The documented `mmastrac/djev` path starts a compatible vLLM server and a schema wrapper. The wrapper seeds an answer canvas and reads distributions from designated slots; changing this inference path does not train new weights. Its README also identifies optional features that depend on outstanding engine changes, so pin compatible code instead of assuming any vLLM release works. [Runtime documentation](https://github.com/mmastrac/djev)

For hosted experimentation, `taeold/djev-run` documents Cloud Run with an RTX PRO 6000 GPU, GCS weight storage, and a container supporting `/v1/systemone`. The example deployment limits context to 4,096 despite the base model's larger specification. Follow the repository's current deployment recipe and query the returned service URL; project permissions, billing, storage, and GPU quota are prerequisites. [Cloud deployment](https://github.com/taeold/djev-run)

I did not find a verified end-to-end RLCD fine-tuning recipe for this diffusion backbone. Google's generic Gemma tuning ecosystem is not evidence that a causal-LM SFT or GRPO script works unchanged on DiffusionGemma. Training it would require a compatible diffusion objective and implementation; start by evaluating the unchanged structured-read baseline. [Google architecture documentation](https://ai.google.dev/gemma/docs/diffusiongemma)

## If you need a hosted custom RLCD-style job

Hugging Face Jobs and Google CustomJob are the clearest general infrastructure routes: package the inspected trainer and pinned dependencies, put data in accessible storage, supply token/service-account permissions, choose GPUs, submit the job, monitor logs, and persist artifacts. This is custom training on a platform, not a provider-certified implementation of TypeSafe's method. HF exposes `hf jobs` and an HTTP API; Google supports custom-container worker pools through `gcloud ai custom-jobs create`. [HF job interface](https://huggingface.co/docs/hub/jobs-reference), [Google job configuration](https://docs.cloud.google.com/vertex-ai/docs/training/create-custom-job)

My suggested order is **freeze evaluation → collect Jev and untuned open-model baselines → run one Laya adaptation or Tev SFT → calibrate and compare → consider custom RL only if it adds measurable value**. Budget training, inference hosting, and dataset labeling separately.
