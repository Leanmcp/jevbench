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
