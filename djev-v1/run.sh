#!/usr/bin/env bash
# User-run launcher for the pinned upstream djev runtime.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p logs
revision=3ce907e6835212f27ee82b4cee9039198c4abe35
container=djev-v1
image=djev-v1:local
export DJEV_MAX_MODEL_LEN="${DJEV_MAX_MODEL_LEN:-4096}"
trap 'echo "Setup failed. Inspect logs/build.log and: sudo docker logs --tail 100 djev-v1" >&2' ERR

command -v git >/dev/null
command -v curl >/dev/null
command -v docker >/dev/null
sudo -v
nvidia-smi
sudo docker info >/dev/null

# The earlier setup may still be building djev-local. Avoid concurrent builds.
if pgrep -f '^docker build -f runtime/Dockerfile -t djev-local' >/dev/null; then
  echo 'Waiting for the earlier djev-local build to finish. Its log is ~/djev-build.log.'
  while pgrep -f '^docker build -f runtime/Dockerfile -t djev-local' >/dev/null; do
    sleep 10
  done
fi

if [ ! -d source ]; then
  git clone https://github.com/Davipar/djev-dev.git source
fi
if [ -n "$(git -C source status --porcelain)" ]; then
  echo 'source/ has local changes; preserve or commit them before rerunning.' >&2
  exit 1
fi
git -C source checkout "$revision"

echo 'Building djev. The previous build layers will be reused when available.'
sudo docker build -f source/runtime/Dockerfile -t "$image" source 2>&1 | tee logs/build.log
sudo docker run --rm --gpus all --entrypoint nvidia-smi "$image"

if sudo docker container inspect "$container" >/dev/null 2>&1; then
  echo "Container $container already exists. No existing container will be replaced."
  echo "Check: sudo docker logs --tail 100 $container"
  echo "To recreate intentionally: sudo docker rm -f $container"
  exit 1
fi

free_kb=$(df -Pk /var/lib/docker | awk 'NR==2 {print $4}')
if [ "$free_kb" -lt 65000000 ]; then
  echo 'Less than approximately 65 GB free on the Docker disk. Free space before downloading weights.' >&2
  exit 1
fi

extra_env=()
if [ -n "${HF_TOKEN:-}" ]; then
  # Propagate the variable without embedding its value in command arguments.
  extra_env+=(--env HF_TOKEN)
fi
echo 'Starting the model with a 4096-token default context. First load downloads weights and compiles kernels.'
sudo --preserve-env=HF_TOKEN docker run -d --name "$container" \
  --gpus device=0 --shm-size=16g \
  -p 127.0.0.1:8000:8000 \
  -e "DJEV_MAX_MODEL_LEN=$DJEV_MAX_MODEL_LEN" \
  "${extra_env[@]}" \
  -v djev-model-cache:/cache "$image"

echo "Follow model progress in a second SSH terminal: sudo docker logs -f $container"
ready=0
for ((attempt=1; attempt<=600; attempt++)); do
  if [ "$(sudo docker inspect -f '{{.State.Running}}' "$container")" != true ]; then
    sudo docker logs --tail 120 "$container" 2>&1 | tee logs/model-failure.log
    echo 'Model process exited. This may be an A100 runtime compatibility or memory issue.' >&2
    exit 1
  fi
  if sudo docker exec "$container" curl -fsS --max-time 3 http://127.0.0.1:8001/v1/models >/dev/null 2>&1; then
    ready=1
    break
  fi
  if (( attempt % 6 == 1 )); then echo "Waiting for model readiness (check $attempt/600)..."; fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "Model startup timed out. Container remains available for inspection: $container" >&2
  exit 1
fi

sudo docker exec -d "$container" sh -c 'exec python3 -m djev --host 0.0.0.0 --port 8000 >/cache/djev-v1-api.log 2>&1'
ready=0
for ((attempt=1; attempt<=60; attempt++)); do
  if curl -fsS --max-time 5 http://127.0.0.1:8000/ready > logs/ready.json; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  sudo docker exec "$container" tail -100 /cache/djev-v1-api.log
  exit 1
fi

echo 'djev is ready. Running one inference check...'
curl --fail-with-body --max-time 120 http://127.0.0.1:8000/v1/request \
  -H 'Content-Type: application/json' \
  --data-binary @smoke.json | tee logs/smoke-response.json
printf '\nVM API docs: http://127.0.0.1:8000/docs\nMac API docs: http://localhost:18000/docs (while the SSH tunnel is connected)\n'
echo 'Stop the service: sudo docker stop djev-v1'
echo 'Stopping the container does not stop GPU VM billing.'
