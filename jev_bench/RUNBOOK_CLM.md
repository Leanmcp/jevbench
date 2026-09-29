# Running CLM yourself, from scratch

Nothing here deletes anything. Every step is idempotent: if a thing is already up, it says so and moves on.

Everything runs from `/Users/ddod/LEANMCP/JEV_RELATED/jev_bench`.

## 0. State as of this writing

VM RUNNING, encoder UP, clm-serve UP, tunnel UP. **If that is still true you can skip to step 5.** Check with:

```bash
curl -s http://127.0.0.1:18700/health | head -c 200
```

An `{"ok":true,...}` means skip ahead. A connection error means start at step 1.

## 1. Log in to Google Cloud

The token expires every few hours. This needs a browser, so run it yourself.

```bash
gcloud auth login
```

Confirm:

```bash
gcloud auth list --filter=status:ACTIVE --format='value(account)'
```

## 2. Start the A100

**This begins GPU billing.** The script also fixes the VM's new IP in `~/.ssh/config`, which changes on every start.

```bash
cd /Users/ddod/LEANMCP/JEV_RELATED/jev_bench/scripts
bash 10_gpu_up.sh
```

Expect: `external IP ...`, `ssh up`, then a GPU/disk/RAM line. About 60 seconds.

## 3. Bring up CLM

Two servers, because CLM is two 75 MB projection heads on a frozen Qwen3-8B encoder:

```bash
bash 30_clm_up.sh
```

Expect, in order: `contrastive-lm ok`, `clm-encoder started`, `encoder ready after Ns`, `clm-serve ready after Ns`, `tunnel up`. First run downloads Qwen3-8B, about 16 GB, roughly 3 minutes. Later runs reuse the `clm-hf-cache` Docker volume and take under a minute.

If it stops at the encoder step:

```bash
ssh djev-a100 'sudo docker logs --tail 40 clm-encoder'
```

If it stops at clm-serve:

```bash
ssh djev-a100 'tail -40 ~/clm/clm-serve.log'
```

## 4. Confirm CLM answers sensibly before spending anything

```bash
curl -s http://127.0.0.1:18700/v1/systemone -H 'Content-Type: application/json' -d '{
  "state": "My credit card was charged twice for one order.",
  "questions": {"team": {"type": "choice", "instructions": "Which team should handle this?",
    "criteria": {"billing": "Charges, invoices and refunds", "engineering": "Outages and broken features"}}}
}' | jq
```

Expect `choice: "billing"` at about 0.996. If this is wrong, stop: the encoder or heads are misconfigured and no benchmark number will be meaningful.

## 5. Run experiments

Everything below is safe to re-run; runs resume rather than restart.

```bash
cd /Users/ddod/LEANMCP/JEV_RELATED/jev_bench
```

**A 20-case trial with full request/response traces:**

```bash
uv run workspace/run_eval.py \
  --endpoint http://127.0.0.1:18700/v1/systemone \
  --label clm-v0.1-8B --no-send-model --save-raw \
  --run-id clm-trial --only prompt_injections --limit 20 --concurrency 8
```

**One slice, with traces:**

```bash
uv run workspace/run_eval.py \
  --endpoint http://127.0.0.1:18700/v1/systemone \
  --label clm-v0.1-8B --no-send-model --save-raw \
  --run-id clm-medmcqa --only medmcqa --concurrency 24
```

**The full suite through the wrapper** (third argument is concurrency):

```bash
cd scripts && bash 40_run_suite.sh clm full 24
```

**Score and report:**

```bash
uv run workspace/score_runs.py --run-id clm-medmcqa
uv run workspace/report.py --run-id clm-medmcqa --compare jev-1.13.0-20260926T133639
```

**The naming-convention probe** (see the open question below):

```bash
uv run workspace/probe_clm_keys.py --slice medmcqa --n 200
```

## 6. Stop billing when done

```bash
cd scripts && bash 90_gpu_down.sh
```

This pulls provenance off the VM, stops the containers, closes tunnels, and stops the instance with `--discard-local-ssd=false` so nothing is lost. It does **not** delete the VM. Disks still incur storage charges while stopped.

## Where the traces are

| What | Where | Notes |
|---|---|---|
| Per-case decisions | `data/runs/<run-id>/predictions.jsonl` | Decision, full probability vector, latency, tokens, errors, timestamp, retry count. One line per case. Local. |
| **Full request and response bodies** | `data/runs/<run-id>/raw.jsonl` | **Only written when you pass `--save-raw`.** This is new; earlier runs in this repo do not have it. |
| Run configuration | `data/runs/<run-id>/meta.json` | Endpoint, label, options, concurrency, slices, first start time, resume count |
| Metrics | `data/runs/<run-id>/scores.json` | Every metric plus the stated conventions |
| Report | `reports/RESULTS_<run-id>.md` | Tables with auto-generated caveats |
| CLM server log | VM `~/clm/clm-serve.log` | Pulled into `provenance/vm/` by `90_gpu_down.sh` |
| Encoder log | VM `docker logs clm-encoder` | Pulled by `90_gpu_down.sh` |
| Resolved Python versions | VM `~/clm/uv.lock` | Pulled by `90_gpu_down.sh` as `clm-uv.lock` |

**Answering the question directly: no, traces were not being logged remotely, and raw bodies were not being saved at all.** Only parsed fields went to `predictions.jsonl`. `--save-raw` now captures the exact request and response per case so a disputed number can be traced to the bytes that produced it. The server-side logs live on the VM and are only collected when `90_gpu_down.sh` runs, so run that rather than stopping the VM by hand.

## Open question: do not publish any CLM number yet

CLM scores **17.0% on MedMCQA**, below the 25% chance floor, at 34/200 which is 2.6 standard deviations below chance. What has been ruled out:

- **Not concurrency.** Concurrency 8 and 24 give byte-identical 34/200.
- **Not a harness bug.** Single-shot requests agree with the batch run on every case checked.
- **Not collapsed output.** Predictions spread across all four letters (46/40/57/57) with 200 distinct probability vectors, and permuted twins show the same values correctly reshuffled.
- **Not cache eviction.** 0 evictions, 0.77 hit rate, 15,802 of 727,119 slots used.
- **Not the criterion naming convention.** All three conventions (letters with text descriptions, text as name, text as both) give exactly 17.0%.
- **Not a broken server.** Its own examples answer correctly, including a real MedMCQA case answered correctly at 0.85 confidence.

Two live hypotheses remain. Either CLM is genuinely weak on knowledge multiple choice, which is plausible because it is a state-action matcher whose published strengths are tool-calling and verification rather than exams, or our question framing suits the other three models and not a dual encoder. Below-chance rather than at-chance is the part that still needs explaining: it suggests a systematic preference for a property that correlates with distractors.

Next diagnostic: run `--save-raw` on 50 cases and read the actual bodies, and compare against CLM's `/v1/rank` endpoint, whose expected body is `{context, question, answers: [...]}` rather than the systemone schema. Ranking answer strings directly may be the interface CLM is actually built for, in which case the multiple-choice slices need a rank-based adapter and that difference is itself a finding worth reporting.
