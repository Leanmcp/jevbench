#!/usr/bin/env bash
# Shared configuration for the jev-bench GPU pipeline. Sourced, not executed.
#
# Every value here was verified against the live project on 2026-09-26. Change
# these rather than editing the numbered scripts.

PROJECT="meta-chalice-499205-b0"
ZONE="us-central1-a"
INSTANCE="rl-arithmetic-a100-80gb"   # a2-ultragpu-1g: 1x A100 80GB, 12 vCPU, 170GB RAM
SSH_HOST="djev-a100"                 # ~/.ssh/config entry, LocalForward 18000 -> 8000
LOCAL_PORT=18000
REMOTE_PORT=8000

# djev runtime. The 8192 context is deliberate: the longest built case is ~3.1k
# estimated tokens, and KV cache holds 124,469 tokens, so raising max_model_len
# from the launcher's 4096 default costs no memory and only lowers max
# concurrency from 20x to 15x.
export DJEV_MAX_MODEL_LEN=8192
DJEV_DIR="~/djev-v1"

# ssh for control commands: ClearAllForwardings stops every control connection
# from fighting the dedicated tunnel for port 18000.
SSH_CTL=(ssh -o BatchMode=yes -o ClearAllForwardings=yes -o ConnectTimeout=20 "$SSH_HOST")

BENCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

say() { printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

# --- CLM (Contrastive Language Model, Stanford/NVIDIA) -----------------------
# CLM-v0.1-8B is two projection heads (75 MB) on a FROZEN Qwen3-8B encoder, so
# two servers are needed: a vLLM pooling server for the encoder, and clm-serve
# for the heads. clm-serve exposes POST /v1/systemone with the same wire schema
# as Jev, so the harness needs no new client.
CLM_HEAD_REPO="Contrastive-LM/CLM-v0.1-8B"
CLM_HEAD_REVISION="e939398d4556fcd9400c76fa8c5a513202f42b0a"
CLM_ENCODER_MODEL="Qwen/Qwen3-8B"
CLM_ENCODER_PORT=8090
CLM_API_PORT=8700
CLM_LOCAL_PORT=18700              # Mac side of the tunnel
# Their launch script defaults to 2048, which would truncate our ATBench cases
# and recreate the Laya context confound. 8192 matches what we gave djev.
# Caveat to report: the heads were precomputed at 2048, so longer states may be
# out of distribution even when they fit.
CLM_MAX_MODEL_LEN=8192
CLM_GPU_UTIL=0.45
# vLLM image already cached on the VM; pinned so a rebuild is reproducible.
VLLM_IMAGE="vllm/vllm-openai:nightly-dee37d89115db4c94a820a79a78a7828e141c910"
