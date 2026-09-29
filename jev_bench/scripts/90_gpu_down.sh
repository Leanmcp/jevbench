#!/usr/bin/env bash
# Stop everything and end GPU billing. Stops the instance; does NOT delete it.
#
#   bash 90_gpu_down.sh
#
# Stopping a container does not stop GPU billing. Only the instance stop does.
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/00_config.sh"

say "pulling serving provenance before shutdown"
mkdir -p "$BENCH_DIR/provenance/vm"
"${SSH_CTL[@]}" '
  mkdir -p /tmp/prov && cd /tmp/prov
  for c in djev-v1 clm-encoder; do
    sudo -n docker inspect "$c" > "inspect-$c.json" 2>/dev/null || true
    sudo -n docker logs --tail 2000 "$c" > "logs-$c.txt" 2>&1 || true
  done
  cp ~/clm/clm-serve.log . 2>/dev/null || true
  cp ~/clm/uv.lock ./clm-uv.lock 2>/dev/null || true
  nvidia-smi > nvidia-smi.txt 2>&1
  sudo -n docker images --digests --format "{{.Repository}}:{{.Tag}} {{.Digest}}" > docker-images.txt 2>/dev/null || true
' || true
rsync -az -e "ssh -o BatchMode=yes -o ClearAllForwardings=yes" "$SSH_HOST":/tmp/prov/ "$BENCH_DIR/provenance/vm/" || true

say "stopping containers"
"${SSH_CTL[@]}" 'sudo -n docker stop djev-v1 clm-encoder 2>/dev/null; pkill -f clm-serve 2>/dev/null; true' || true

say "closing tunnels"
pkill -f "ssh.*-N.*${SSH_HOST}" 2>/dev/null || true

say "stopping the instance (this is what ends GPU billing)"
# --discard-local-ssd=false preserves the Local SSD contents; gcloud requires an
# explicit choice when a Local SSD is attached.
gcloud compute instances stop "$INSTANCE" --project="$PROJECT" --zone="$ZONE" \
  --discard-local-ssd=false >/dev/null
say "instance is now $(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='value(status)')"
say "note: TERMINATED means stopped. Disks still incur storage charges."
