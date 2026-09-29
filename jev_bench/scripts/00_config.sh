#!/usr/bin/env bash
# Shared configuration for the jev-bench GPU pipeline. Sourced, not executed.
#
# Cloud details are never stored in this repository. Set them in your shell or
# in jev_bench/.env (git-ignored; copy jev_bench/.env.example to start):
#   GCP_PROJECT   Google Cloud project that owns the VM
#   GCP_ZONE      zone of the VM
#   GCP_INSTANCE  name of the VM (one A100 80GB)
#   SSH_HOST      ~/.ssh/config entry for the VM, with LocalForward 18000 -> 8000

_env_file="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env"
# shellcheck disable=SC1090
[ -f "$_env_file" ] && source "$_env_file"
for _v in GCP_PROJECT GCP_ZONE GCP_INSTANCE SSH_HOST; do
  if [ -z "${!_v:-}" ]; then
    echo "missing $_v: set it in your shell or in jev_bench/.env (see .env.example)" >&2
    return 1 2>/dev/null || exit 1
  fi
done

PROJECT="$GCP_PROJECT"
ZONE="$GCP_ZONE"
INSTANCE="$GCP_INSTANCE"
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
