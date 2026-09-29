# djev-v1 on your A100

From your Mac: `ssh "$SSH_HOST"` (see `jev_bench/.env.example`).

On the VM:

```bash
cd ~/djev-v1
bash run.sh
```

The script builds the pinned djev image, reuses previous build layers where possible, downloads model weights, waits for the backend, starts the API, then runs one real security classification request. It waits for the previous djev-local build if that build is still running. No optional Node playground is installed. First startup can take many minutes.

The VM (one A100 80 GB) and its CUDA-13-compatible driver are verified. GPU access inside Docker is verified. Actual djev inference on the A100 is still unverified until this script succeeds.

View progress from another SSH terminal:

```bash
tail -f ~/djev-v1/logs/build.log
sudo docker logs -f djev-v1
```

After readiness, open http://localhost:18000/docs on your Mac while `ssh "$SSH_HOST"` keeps the tunnel open. Without a tunnel, the API is accessible only on the VM at http://127.0.0.1:8000/docs. Do not open a public firewall port for it.

If startup fails, inspect `sudo docker logs --tail 120 djev-v1`. For API errors: `sudo docker exec djev-v1 tail -100 /cache/djev-v1-api.log`. The script leaves failed containers intact for diagnosis. A rerun will not replace an existing `djev-v1` container; intentionally remove it first if appropriate.

Stop the service with `sudo docker stop djev-v1`. To stop GPU compute billing, run this on your Mac:

```bash
gcloud compute instances stop "$GCP_INSTANCE" --project="$GCP_PROJECT" --zone="$GCP_ZONE"
```

Persistent storage still incurs charges. The model cache is retained in Docker volume `djev-model-cache`.
