#!/usr/bin/env bash
# Bring up CLM-v0.1-8B on the VM and tunnel it to the Mac.
#
#   bash 30_clm_up.sh
#
# Two servers, because CLM is heads on a frozen encoder:
#   1. Qwen3-8B pooling server (Docker, pinned vLLM image) on VM:8090
#   2. clm-serve head server (uv-managed venv) on VM:8700
# Then a tunnel so the harness can reach VM:8700 at localhost:18700.
#
# Idempotent: skips whatever is already healthy.
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/00_config.sh"

say "1/5 installing uv and the contrastive-lm package on the VM"
"${SSH_CTL[@]}" "
  set -Eeuo pipefail
  export PATH=\"\$HOME/.local/bin:\$PATH\"
  command -v uv >/dev/null || curl -fsSL https://astral.sh/uv/install.sh | sh
  mkdir -p ~/clm && cd ~/clm
  # A project-local venv, no global pip, versions resolved and locked by uv.
  [ -f pyproject.toml ] || uv init --bare --python 3.12 >/dev/null
  uv add contrastive-lm huggingface-hub 2>&1 | tail -3
  uv run python -c 'import clm; print(\"contrastive-lm ok\")'
"

say "2/5 starting the Qwen3-8B pooling encoder (Docker, pinned image) on port $CLM_ENCODER_PORT"
"${SSH_CTL[@]}" "
  set -Eeuo pipefail
  if sudo -n docker ps --format '{{.Names}}' | grep -qx clm-encoder; then
    echo 'clm-encoder already running'
  else
    sudo -n docker rm -f clm-encoder 2>/dev/null || true
    # Last-token pooling and prefix caching match how the heads were precomputed.
    # enforce-eager keeps startup short and memory modest.
    sudo -n docker run -d --name clm-encoder --gpus device=0 --shm-size=8g \
      -p 127.0.0.1:${CLM_ENCODER_PORT}:${CLM_ENCODER_PORT} \
      -v clm-hf-cache:/root/.cache/huggingface \
      ${VLLM_IMAGE} \
      --model ${CLM_ENCODER_MODEL} --served-model-name qwen3-8b \
      --runner pooling --enforce-eager --enable-prefix-caching \
      --max-model-len ${CLM_MAX_MODEL_LEN} \
      --gpu-memory-utilization ${CLM_GPU_UTIL} \
      --max-num-seqs 32 --port ${CLM_ENCODER_PORT} --host 0.0.0.0
    echo 'clm-encoder started'
  fi
"

say "3/5 waiting for the encoder (first run downloads Qwen3-8B, about 16 GB)"
"${SSH_CTL[@]}" "
  for i in \$(seq 1 240); do
    if curl -fsS --max-time 5 http://127.0.0.1:${CLM_ENCODER_PORT}/v1/models >/dev/null 2>&1; then
      echo \"encoder ready after \$((i*10))s\"; exit 0
    fi
    if ! sudo -n docker ps --format '{{.Names}}' | grep -qx clm-encoder; then
      echo 'ENCODER EXITED. Last 40 lines:'; sudo -n docker logs --tail 40 clm-encoder; exit 1
    fi
    [ \$((i % 6)) -eq 1 ] && echo \"  waiting (\$((i*10))s)...\"
    sleep 10
  done
  echo 'encoder timed out'; sudo -n docker logs --tail 40 clm-encoder; exit 1
"

say "4/5 starting clm-serve (the heads) on port $CLM_API_PORT"
"${SSH_CTL[@]}" "
  set -Eeuo pipefail
  export PATH=\"\$HOME/.local/bin:\$PATH\"
  cd ~/clm
  if curl -fsS --max-time 5 http://127.0.0.1:${CLM_API_PORT}/health >/dev/null 2>&1; then
    echo 'clm-serve already healthy'
  else
    # Do NOT pkill by name here. This shell's own command line contains the
    # server's name (in the launch line below), so any -f pattern that matches
    # the server also matches this shell and kills its own parent. Kill only
    # whatever holds the port instead, identified by the port and nothing else.
    # The '|| true' is required: with pipefail set, grep finding nothing exits 1,
    # which under 'set -e' aborts this whole shell before the server ever starts.
    held=\$(ss -ltnpH \"sport = :${CLM_API_PORT}\" 2>/dev/null | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2 || true)
    if [ -n \"\${held:-}\" ]; then echo \"killing stale pid \$held on port ${CLM_API_PORT}\"; kill \"\$held\" 2>/dev/null || true; sleep 2; fi
    : > ~/clm/clm-serve.log
    CLM_EMB_URL=http://127.0.0.1:${CLM_ENCODER_PORT}/v1/embeddings \
    nohup setsid ~/clm/.venv/bin/clm-serve --port ${CLM_API_PORT} \
      >> ~/clm/clm-serve.log 2>&1 < /dev/null &
    disown || true
    for i in \$(seq 1 60); do
      curl -fsS --max-time 5 http://127.0.0.1:${CLM_API_PORT}/health >/dev/null 2>&1 && { echo \"clm-serve ready after \$((i*5))s\"; exit 0; }
      sleep 5
    done
    echo 'clm-serve did not become healthy. Last 40 lines:'; tail -40 ~/clm/clm-serve.log; exit 1
  fi
"

say "5/5 opening the tunnel localhost:${CLM_LOCAL_PORT} -> VM:${CLM_API_PORT}"
pkill -f "ssh.*-N.*-L ${CLM_LOCAL_PORT}:" 2>/dev/null || true
# NOTE: no ClearAllForwardings here. That option clears forwardings given on the
# command line as well as in config, so it would delete the -L below. The ssh
# config entry also forwards 18000; that is harmless and left in place.
nohup ssh -o BatchMode=yes -o ServerAliveInterval=30 \
  -N -L "${CLM_LOCAL_PORT}:127.0.0.1:${CLM_API_PORT}" \
  "$SSH_HOST" > /tmp/clm-tunnel.log 2>&1 &
for i in $(seq 1 15); do
  if curl -fsS --max-time 4 "http://127.0.0.1:${CLM_LOCAL_PORT}/health" >/dev/null 2>&1; then
    say "tunnel up"; break
  fi
  sleep 2
done

say "CLM endpoint: http://127.0.0.1:${CLM_LOCAL_PORT}/v1/systemone"
say "next: bash 40_run_suite.sh clm"
