#!/usr/bin/env bash
# Start the A100 VM and make it reachable. Idempotent: safe to re-run.
#
#   bash 10_gpu_up.sh
#
# GPU billing starts here. 90_gpu_down.sh stops it.
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/00_config.sh"

status() { gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='value(status)' 2>/dev/null; }

say "instance $INSTANCE is $(status)"
if [ "$(status)" != "RUNNING" ]; then
  say "starting (GPU billing begins now)"
  gcloud compute instances start "$INSTANCE" --project="$PROJECT" --zone="$ZONE" >/dev/null
fi

IP=$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" \
      --format='value(networkInterfaces[0].accessConfigs[0].natIP)')
say "external IP $IP"

# The ephemeral IP changes on every start, so keep ~/.ssh/config in step.
CURRENT=$(awk -v h="$SSH_HOST" '$1=="Host" && $2==h {f=1; next} f && $1=="HostName" {print $2; exit}' ~/.ssh/config)
if [ "$CURRENT" != "$IP" ]; then
  cp ~/.ssh/config "$HOME/.ssh/config.bak.$(date +%s)"
  sed -i '' "s/HostName ${CURRENT}/HostName ${IP}/" ~/.ssh/config
  say "updated ~/.ssh/config: $CURRENT -> $IP (backup kept)"
fi

say "waiting for sshd"
for i in $(seq 1 60); do
  if ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ClearAllForwardings=yes \
         -o ConnectTimeout=10 "$SSH_HOST" 'true' 2>/dev/null; then
    say "ssh up after ${i} attempt(s)"; break
  fi
  sleep 5
done

"${SSH_CTL[@]}" '
  echo "GPU:   $(nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader)"
  echo "disk:  $(df -h / | awk "NR==2 {print \$4\" free of \"\$2}")"
  echo "ram:   $(free -g | awk "NR==2 {print \$7\" GB available\"}")"
  echo "containers: $(sudo -n docker ps --format "{{.Names}}" | tr "\n" " ")"
'
say "up. next: start djev on the VM (see djev-v1/README.md), then bash 40_run_suite.sh djev"
