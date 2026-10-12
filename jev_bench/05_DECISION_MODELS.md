# More decision models: OpenRouter, plus the two open d1 weights

Checked 11 October 2026. Code is in place; nothing below has been run yet.

## Where each model runs

Hosted wherever possible. OpenRouter's alpha Decisions endpoint,
`POST https://openrouter.ai/api/alpha/decisions`, takes the same
`{model, state, questions}` body the harness already sends and answers in the
same `{answers, usage}` shape as Jev, so the existing parser reads it unchanged.
One `OPENROUTER_API_KEY` covers every hosted model. The only weights the
benchmark runs itself are the two small Liquid d1 checkpoints, which no API
serves; both fit on a laptop.

| Model | Route | Input $/M tokens | Licence |
|---|---|---|---|
| `cloudflare/clef` (27B) | OpenRouter | 0.24 | Apache 2.0 ([card](https://huggingface.co/Cloudflare/clef)) |
| `cloudflare/clef-flash` (9B) | OpenRouter | 0.038 | Apache 2.0 ([card](https://huggingface.co/Cloudflare/clef-flash)) |
| `cloudflare/clef-omni` | OpenRouter | 0.15 | Apache 2.0 ([card](https://huggingface.co/Cloudflare/clef-omni)) |
| `perplexity/pplx-decider-v1.1-27b` | OpenRouter | 0.02 | Apache 2.0 ([card](https://huggingface.co/perplexity-ai/pplx-decider-v1.1-27b)) |
| `openai/gpt-6-luna-decisions` | OpenRouter | 0.10 | not checked |
| `microsoft/microsoft-decision-1` | OpenRouter | 0.042 | not checked |
| `upstage/solar-decide`, `solar-decide-flash` | OpenRouter | 0.05 | not checked |
| `nace-ai/drex-v1.5` | OpenRouter | 0.04 | not checked |
| `inception/mercury-decide` | OpenRouter | 0.02 | not checked |
| `togethercomputer/tev1-4b-experimental` | OpenRouter | 0.042 | not checked |
| `jaredpalmer/kev-4b` | OpenRouter | 0.042 | not checked |
| `respan/span-01` | OpenRouter | 0.02 | not checked; listed with context length 0 |
| `LiquidAI/d1-3B` (3.1B) | local, `serve_d1_local.py` | free | LFM Open License v1.0 (`lfm1.0` on the card) |
| `LiquidAI/d1-omni-600M` (587M) | local, `serve_d1_local.py` | free | LFM Open License v1.0 |

Prices are from `https://openrouter.ai/api/v1/models?output_modalities=decisions`
on the date above; output tokens are free on every one. They match the vendors'
direct prices where checked (Clef and Clef-flash on Workers AI, Perplexity's
Decisions API). Every prediction row stores OpenRouter's billed `cost_usd`, so
the real spend comes from the data afterwards.

The LFM Open License v1.0 is based on Apache 2.0 but is not Apache 2.0: use is
free under USD 10M annual revenue and needs a paid licence above it. Its
published summary places no restriction on publishing benchmark results. The
hosted Liquid d1 already run in `liquid-d1-full` is a service, covered by
Liquid's service terms rather than this licence; see `03_LIQUID_D1.md`.

## What a full run costs

A full text run is about 8,000 requests. Existing runs counted 3.0M input
tokens (Liquid d1) and 6.0M (Jev) for the same cases, because tokenizers differ,
so expect each model to land between those.

| Model | One full run |
|---|---|
| Clef | USD 0.72 to 1.44 |
| Clef-omni | 0.45 to 0.90 |
| GPT-6 Luna Decisions | 0.30 to 0.60 |
| Solar Decide, either | 0.15 to 0.30 |
| the 0.04 group | 0.12 to 0.25 |
| Clef-flash | 0.11 to 0.23 |
| pplx-decider v1.1, Mercury, Span | 0.06 to 0.12 |

All thirteen OpenRouter models together come to roughly USD 3 to 6.

## Run order

The simplest route is the matrix, which runs only the cells that are missing:

```bash
time uv run workspace/matrix.py
```

The per-model scripts below do the same for one model at a time. From
`jev_bench/`, with `OPENROUTER_API_KEY` exported in the shell:

```bash
# 1. build every request for one model, send nothing
bash scripts/43_run_openrouter.sh dry-run cloudflare/clef

# 2. nine real requests per model: Noul, Score and 77-way Choice
time bash scripts/43_run_openrouter.sh trial all

# 3. read the trial scores, then the full suites
time bash scripts/43_run_openrouter.sh full all
```

The local d1 weights, two shells, one model at a time:

```bash
uv run workspace/serve_d1_local.py --model LiquidAI/d1-3B          # shell 1
time bash scripts/44_run_d1_local.sh trial d1-3B                    # shell 2
time bash scripts/44_run_d1_local.sh full d1-3B
# then stop the server and repeat with LiquidAI/d1-omni-600M and d1-omni-600M
```

`serve_d1_local.py` carries its own dependencies as inline script metadata, so
`uv run` builds a separate environment and torch never enters the harness's
lockfile. It picks CUDA, then Apple MPS, then CPU. Pass `--revision <hash>` to
pin the checkpoint for a reproducible run.

## Checks before quoting a number

- The trial must parse on all three types. A model that rejects Noul `criteria`
  or object states fails here, on nine requests; record a separate protocol
  variant rather than editing the cases.
- `provider_reported` names the upstream that served each row. A model served
  by more than one provider is not one fixed system; pin it with OpenRouter's
  `provider` field if that happens.
- Image slices are skipped for now. Clef, Clef-omni, pplx-decider and GPT-6
  Luna accept images on OpenRouter, but the image field is not wired yet.
- Hosted latency includes network and an unknown serving stack. It is not a
  speed comparison.
