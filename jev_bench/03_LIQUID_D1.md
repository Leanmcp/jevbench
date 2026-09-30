# Liquid D1 evaluation and Google Cloud plan

Checked 30 September 2026. Integration implemented; live inference and ranking
have not been run. No new dependencies are required.

## Availability and licence

The [D1 documentation](https://docs.liquid.ai/lfm/models/decision-models)
documents `POST https://api.liquid.ai/decisions/v1/systemone`, model `d1:free`,
and a bearer key created at [Liquid Console](https://console.liquid.ai/), under
Dashboard > API Keys after joining an organization. It supports Noul, Choice
and Score. The [model matrix](https://docs.liquid.ai/lfm/models/complete-library)
lists D1 as API-only and not trainable, without downloadable model formats.
There is no documented D1 GPU runtime or checkpoint to deploy ourselves.

D1 should currently be recorded as a proprietary hosted service, with no
verified open-weight licence. Liquid's public
[service terms](https://www.liquid.ai/terms-conditions) grant limited, revocable
service access; verify the actual agreement presented by the D1 console for
your account, including benchmark publication and prediction redistribution.
Those public terms are dated 2024 and are not a D1-specific model licence.

Liquid also publishes the [LFM Open License v1.0](https://www.liquid.ai/lfm-license).
It is based on Apache 2.0 with a commercial revenue restriction, not Apache 2.0
itself: commercial users exceeding $10M annual revenue need a separate licence.
It includes research/nonprofit provisions and attribution requirements.
No D1 weight release was found assigning that licence to D1. Do not infer a
right to download or self-host D1 from the general LFM licence page.

## Run locally or on a Google Cloud CPU VM

Use the same pinned cases as the existing evaluations. The harness preserves
state, question instructions and criteria, and changes the model and endpoint.
The existing parser handles the documented response format. No SDK is needed.
The hosted alias is not an immutable revision: retain run timestamps and
`model_reported`, and request a pinned version from Liquid for reproducibility.

Run these commands yourself from the repository root:

```bash
cd jev_bench
uv sync --locked
uv run workspace/test_liquid.py
uv run workspace/verify_cases.py
bash scripts/41_run_liquid.sh dry-run
```

Set `LIQUID_API_KEY` securely in the shell running the harness, then run:

```bash
bash scripts/41_run_liquid.sh trial
# Inspect reports/RESULTS_liquid-d1-trial.md and the trial predictions first.
bash scripts/41_run_liquid.sh full
uv run workspace/paired_bootstrap.py \
  --runs D1=liquid-d1-full \
  --runs Jev=jev-1.13.0-20260926T133639 \
  --runs djev=djev-full \
  --runs Laya=laya-en-full
```

If cases are absent, follow `01_DOWNLOAD.md` and `02_RUNNING.md` first.
The trial covers Noul, Score and 77-way Choice. Specifically verify that D1
accepts the existing Noul `criteria` and object-valued state: Liquid's examples
omit Noul criteria and mostly send string states. Do not silently remove or
rewrite benchmark inputs if rejected; record a separate protocol variant if
an adaptation is necessary. Confirm rate limits and context/choice limits with
Liquid; the script defaults to concurrency 8 and uses existing retry/backoff.
Override with `LIQUID_CONCURRENCY=16 bash scripts/41_run_liquid.sh full`.
If rate-limit errors increase, lower concurrency. Stop the existing process
before resuming the same run ID; never run two writers against the same run.
Concurrency changes are retained in metadata and new prediction rows record
their client concurrency. A resumed run with changed concurrency has mixed
latency conditions and must not be described as a fixed-concurrency speed test.
Image cases are excluded because D1 image input is not documented.

Re-running a run ID resumes successful predictions and retries failed parsing.
Use `LIQUID_RUN_ID=liquid-d1-YYYYMMDD` for a fresh evaluation. The runner rejects
reuse of a run ID for another endpoint/model/options. Do not change the cases
under a resumed run. Keys are never recorded in metadata and both providers'
keys are scrubbed from errors. Raw request recording remains opt-in.

For GCP today, run this same harness on a CPU Compute Engine VM with outbound
HTTPS to Liquid. Transfer the pinned cases and repository revision, provide
the key through your existing secret process, run the dry-run/trial/full steps,
then copy back `data/runs/liquid-d1-*` and `reports/RESULTS_liquid-d1-*.md`.
This hosts the benchmark client on GCP; inference still runs at Liquid.
No GPU, model container, inbound API port, or SSH model tunnel is needed.

## GPU deployment, conditional on Liquid granting access

Before a real D1 deployment can be implemented, obtain from Liquid:

1. D1 weights with a fixed revision/hash, or a supported inference container
   with an immutable digest and registry access.
2. Self-hosting licence terms and permission to publish benchmark outputs.
3. Supported GPU, VRAM, precision, CUDA/driver/runtime versions, maximum
   context/choices, and the actual serving entry point and request contract.

Then reuse the djev approach: select a compatible GCP GPU VM from the supplied
requirements (do not assume D1 needs or supports the existing A100 80GB), pin
the container/checkpoint, persist its cache, bind the decision service to
loopback, and tunnel it over SSH. Adapt its real serving interface to the
benchmark contract if needed. Capture the image digest, model revision,
runtime configuration and `nvidia-smi` in provenance. Run the same trial and
text suite, then stop the GPU VM using the existing shutdown workflow.
No GPU has been provisioned and no speculative D1 serving command is supplied.

## Ranking

Report accuracy, Brier/NLL/calibration and ordinal metrics on matching text
case IDs, with paired family bootstrap comparisons. Check coverage and errors
before claiming a rank. Hosted latency includes network overhead and has
unknown hardware, so it is not a controlled GPU speed comparison. Keep D1's
zero output-token counts intact. Do not update the paper or published ranking
until actual predictions have been scored.
