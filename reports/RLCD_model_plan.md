# Training a decision model that reads everything and can deliberate

Plan, 26 September 2026. No training run, dataset or result exists yet. Prices and dataset availability below are marked where unverified. Evidence cited from measured runs in [jev_bench](../jev_bench/), specifically `data/runs/{jev-1.13.0-*,laya-en-full,djev-full,djev-multimodal}/scores.json`.

Related: [benchmark and paper plan](Benchmark_and_paper_plan.md) · [prior work](Benchmark_prior_work.md) · [harness](../jev_bench/02_RUNNING.md).

## 1. Is it worth it

Yes, but not as "another Jev." Training a general typed-decision model to compete with Jev 1.13 is a losing proposition: it is better on every general slice we measured and you would be chasing a moving vendor with a fraction of the data. The case for a new model rests entirely on picking a limitation the incumbents structurally cannot fix without retraining, and owning it.

The two you named are exactly those, and the measured evidence says so.

**Limitation A: bounded input.** Same 500 ATBench trajectories, three models, one question each:

| Model | Mean input tokens seen | Accuracy |
|---|---:|---:|
| Laya 421M (512-token budget) | 512 | 65.4% |
| djev-0.1 (DiffusionGemma 26B-A4B, 8192 set by us) | 1,988 | 75.8% |
| Jev 1.13 | 2,253 | 93.0% |

Every model here is reading a **single agent trajectory** of roughly two thousand tokens. A detection-engineering workload is five to eight orders of magnitude larger: a day of Sysmon from one host, a week of VPC flow logs, a malware sample's full behavioural trace. None of these models can be pointed at that. The ceiling is not a tuning parameter, it is the architecture's context window, and both vendors would have to retrain to move it.

**Limitation B: no deliberation.** djev's API fixes `steps` at 1. It is one denoising read of an answer canvas, and that is the whole product thesis: speed through doing less output work. It also means there is no mechanism to spend more compute on a hard case than an easy one. Our numbers show the cost of that: djev's ECE on ATBench is 0.19, and moving nothing but the threshold lifts it from 75.8% to 80.6%. The model has signal it cannot act on and no way to look again.

**What makes this a contribution rather than an engineering exercise** is that both limitations have the same shape: they are about *allocating* computation, over input and over depth. A model that decides how much to read and how long to think, while staying calibrated, is a different object from Jev, not a worse copy of it.

**The honest counter-argument.** You do not need a new model to get long-context detection. A cheap pre-filter plus an existing model over survivors is the industry answer and it works. The research question is whether a single end-to-end calibrated model beats a cascade of heuristics at matched cost, and **you should be willing to publish a negative result there.** If the cascade wins, that is a useful finding and a cheap paper. Decide this before spending on scale, not after.

## 2. Contribution A: one calibrated bit from unbounded input

### The task, stated precisely

Given a bag of evidence `X = {x_1 ... x_N}` with N unbounded (log lines, events, files, flow records), emit:

1. `p(bag contains a malicious/anomalous instance)`, calibrated
2. the instances responsible, ranked

This is **multiple-instance learning**, and naming it that matters: it is a solved formalism with known pitfalls, so you inherit the literature instead of rediscovering it. The bag label is an existential quantifier. One malicious line makes the bag positive; ten thousand benign lines do not make it negative.

### Architecture

Do not pretrain a long-context backbone. The cost is not justified and it is not where the contribution is.

```
chunk encoder (frozen, small)  ->  per-chunk representation h_i
                               ->  per-chunk logit s_i
attention-based aggregator     ->  a_i = softmax over chunks (gives localisation)
calibrated bag head            ->  p(bag) conditioned on N
```

Three design commitments, each with a reason:

**Noisy-OR, not mean pooling.** Mean pooling over 10,000 chunks drowns a single positive; it has the wrong semantics for an existential question. Noisy-OR, `p_bag = 1 - prod_i (1 - p_i)`, matches the task.

**Condition the head on bag size, or noisy-OR destroys your calibration.** This is the trap and it is worth the paper's sharpest paragraph. With a per-chunk false-positive probability of 0.001, a 10,000-chunk bag gives `1 - 0.999^10000 = 0.99995`. Every large bag becomes positive. It is the multiple-comparisons problem wearing a probabilistic hat. The fix is to learn the aggregation conditioned on N, calibrate per bag-size bucket, and **report reliability curves stratified by N**, not pooled. Any paper in this space that reports one ECE number over mixed bag sizes is hiding this.

**Attention weights are a product feature, not an interpretability garnish.** A detection engineer cannot act on "0.87 malicious." They need the three lines to look at. Localisation quality is therefore a headline metric, not an appendix: report precision@k over instances given a positive bag, against instance-level labels where they exist.

### Why this is cheap to pilot

Freeze the encoder and **cache the per-chunk representations once**. The aggregator is then a few million parameters training on cached vectors, which is minutes on a laptop per configuration. The entire cost of contribution A is one inference pass over the corpus, and after that you can iterate on aggregation, bag-size conditioning and calibration for free. This is the single most important budget fact in this document.

## 3. Contribution B: giving a System 1 model a System 2 mode

### Four mechanisms, ranked by cost and by how much they would teach you

| Mechanism | What it is | Cost | Verdict |
|---|---|---|---|
| Multi-sample averaging | djev's existing `samples` 1-4, averaging independent one-step reads | Free, today | **Do this first.** It is the baseline any deliberation claim must beat, and we ran everything at `samples=1`, so the number is unknown. |
| More denoising steps | djev fixes `steps=1`; a diffusion decision model's natural depth knob | Needs a modified runtime | The most elegant fit. Diffusion gives graded compute for free; the product just chose not to expose it. |
| Latent deliberation slots | k trainable latent positions before the answer canvas, carrying intermediate computation with no verbalisation | Training run | Keeps non-autoregressive speed and calibration. The real contribution candidate. |
| Verbalised reasoning then decide | Generate a rationale, then answer | Large, slow | **Control arm only.** It surrenders the calibration and latency that make this model class worth using. If it wins outright, the honest conclusion is that a small decision model was the wrong bet. |

### The bar a deliberation claim has to clear

Accuracy at **matched average compute**, not matched request count. A model that thinks four times as long and gains three points has not shown deliberation works; it has shown four cheap reads would have too. So:

- Sweep compute per decision, plot accuracy against mean FLOPs
- Compare against the multi-sample baseline at each point on that curve
- Learn a **halting rule** so mean compute stays near System 1 while hard cases get more, then report the compute distribution, not just its mean

### Adaptive depth is the same problem as Contribution A

Both are allocation under a budget, which is why they belong in one model rather than two papers. "How many chunks deserve a second look" and "how long should I think about this chunk" are the same question asked over input and over depth. A shared halting policy over both axes, trained against a cost-aware objective, is a coherent thesis: **budgeted calibrated detection**. That framing is also what stops the paper reading as two unrelated tricks.

## 4. Why RLCD fits this unusually well

RLCD in the literature is Reinforcement Learning from Contrastive Distillation: build preference pairs by prompting a teacher with directionally opposed prompts, then train on the pairs without human labels. Note carefully: **TypeSafe's use of the term for Jev is not something we have reproduced or verified.** Do not describe your objective as "TypeSafe's RLCD." Describe what you actually implement.

The reason it suits detection better than it suits open-ended alignment:

**In detection the contrast is synthesisable with ground truth.** Take a benign log window. Inject a known malicious pattern. You now have a minimally different pair where the label difference is *certain*, not inferred from a teacher's bias. Alignment RLCD has to trust that a "be harmful" prompt actually produced the worse response. You do not. You know, because you did the injection.

That converts the weakest link in RLCD into a strength, and it gives you the controlled-variation structure your benchmark plan already argues for: matched pairs differing in exactly one thing. It also gives unlimited training data from a finite corpus of benign logs plus a finite library of attack patterns.

**The failure mode to design against from day one:** the model learns the injection artefact rather than the malice. If injected lines have different formatting, timestamp spacing, or field order, you have built a formatting detector with excellent metrics. Mitigations are mandatory, not optional: inject with the same tooling that writes benign lines, hold out entire attack families at test time, include **benign lookalikes** (a legitimate admin action that resembles the attack), and keep a real-incident test set that involved no injection at all. If accuracy collapses from the injected test set to the real one, that gap is the finding.

## 5. Training recipe

| Stage | What | Why it is in this order |
|---|---|---|
| 0. Pin the data | Manifest with commit hashes, licences, exposure flags, exactly like [sources.json](../jev_bench/sources.json) | Cost nothing now, saves the paper later |
| 1. Freeze an eval set first | Real incidents, held-out attack families, benign lookalikes, bag sizes spanning 10 to 10^5 | Before any training, or the numbers are unfalsifiable |
| 2. Chunk-level SFT on soft labels | Distil a teacher ensemble's probabilities, not its argmax | Calibration is the product; start it here |
| 3. Train the aggregator on cached representations | Bag-size-conditioned noisy-OR plus attention | Nearly free, and settles feasibility before any expensive stage |
| 4. RLCD on synthesised contrastive pairs | Matched benign/injected bags, held-out attack families | The differentiating stage |
| 5. Separate calibration split | Temperature or vector scaling per bag-size bucket, frozen before test | Choosing thresholds on test is the error we already caught in every model we measured |
| 6. Deliberation arm | Latent slots plus halting rule, trained against a cost-aware objective | Last, because it needs a working single-step model to improve on |

Ablations that decide whether the story is real: no bag-size conditioning; mean pooling instead of noisy-OR; SFT only versus SFT plus RLCD; fixed depth versus learned halting; no benign lookalikes in training.

## 6. Parallel samples: where they are needed and where they are waste

You asked about parallel sampling. There is a sharp distinction worth building the code around.

**For the decision head, do not sample. Enumerate.** The output is a categorical distribution over K labels with K small, 2 to a few hundred. A policy-gradient estimator that samples decisions to estimate expected reward is throwing away an exact computation: with K outcomes you can compute the expected reward and its exact gradient in one pass by enumerating all K. Sampling here adds variance and buys nothing. This is the main reason RL on a typed-decision model is cheaper than RL on a generative model, and it should be stated explicitly in the paper because readers will assume PPO-style rollout costs.

**Sample in parallel where the space is genuinely combinatorial:** trajectories over latent deliberation slots (Contribution B), chunk-selection policies over a bag (which chunks to examine, an ordering problem), and the attacker side of adaptive-attack evaluation. Group-relative advantages over G parallel rollouts is the right tool there, and G is a real hyperparameter.

**At inference,** parallel sampling is djev's `samples` parameter: independent reads averaged. Free variance reduction, and the baseline deliberation must beat.

## 7. Data

Candidates for log and detection work. **None of these were verified live today**, unlike the jev-bench sources; treat every row as a lead to be pinned with a commit hash, licence and row count before use.

| Source | What it gives | Caution |
|---|---|---|
| LogHub (HDFS, BGL, Thunderbird, Spark) | Large real system logs with anomaly labels | Labels are coarse and partly heuristic; check how each was derived |
| EMBER, SOREL-20M | PE malware features and labels at scale | Feature vectors, not raw behaviour; a different task from log triage |
| EVTX-ATTACK-SAMPLES, Security-Datasets | Windows event logs with real attack activity | Small; best as an untouched real-incident test set, never for training |
| CIC-IDS2017, UNSW-NB15 | Labelled network flows | Known label and generation artefacts; widely criticised, cite the critiques |
| Your own telemetry | The only data with real prevalence | Access, privacy and redaction work; also the only route to a genuine deployment claim |

Two rules carried from the benchmark work: real class prevalence in production is wildly imbalanced, so a balanced test set cannot estimate deployment incident rates, and you need a separate prevalence-matched slice for that claim. And every source needs the `exposure` flag, because a public log anomaly set may well be in a base model's pretraining.

## 8. Budget

Assumptions, all of which should be re-checked before committing spend: A100 80GB on-demand at roughly $3 to $4 per hour and H100 at roughly $2 to $3 per hour on the cheaper clouds, **both quoted from memory and unverified**; spot or preemptible at 30 to 50 percent of on-demand; a 4B-active model at order 5,000 tokens per second of prefill throughput on one A100. Verify each before relying on any number in this table.

| Phase | Work | Compute | Cost estimate |
|---|---|---|---:|
| 0 | Pin data, freeze eval set, write adapters | none | $0 |
| 1 | One inference pass to cache chunk representations, pilot scale: 2,000 bags x 50 chunks x 1,000 tokens = 10^8 tokens | ~6 A100-hours | **$20 to $30** |
| 2 | Aggregator and calibration sweeps on cached vectors | laptop | **~$0** |
| 3 | Chunk-level SFT, LoRA on 4B, ~10^8 tokens | 20 to 60 A100-hours | **$80 to $250** |
| 4 | RLCD stage, 3 to 5x the SFT budget | 60 to 300 A100-hours | **$250 to $1,200** |
| 5 | Deliberation arm, three seeds | 50 to 150 A100-hours | **$200 to $600** |
| 6 | Scale-up pass if the pilot works: 20,000 bags x 500 chunks = 10^10 tokens | ~550 A100-hours | **$1,700 to $2,200** |
| 7 | Evaluation API calls for baselines, Jev plus a frontier model | none | **$100 to $400** |

**Credible paper, pilot scale only: roughly $700 to $2,500.** With the scale-up pass and three seeds throughout: **roughly $3,000 to $8,000.** The djev evaluation you just ran cost 51 minutes of A100 time, well under $5, which is the right calibration for how cheap the evaluation half of this is compared with training.

Two ways to cut it materially. Phase 1 and 2 are the whole feasibility question and cost under $30, so **never commit to phases 3 onward before phase 2 has answered the aggregation question.** And a managed LoRA service removes the infrastructure work for stages 3 and 4; pull its live pricing rather than assuming, since per-token training prices move.

## 9. Evaluation

Reuse the harness. It already does the hard parts: one schema across models, full probability vectors persisted, bootstrap CIs grouped by family, both-polarity reporting, contamination flags and automatic caveat generation. Add:

- **Bag-size sweep** as a first-class axis, with reliability curves stratified by N
- **Localisation metrics**, precision@k over instances given a positive bag
- **Compute accounting** per decision, so the deliberation claim can be made at matched FLOPs
- **Prevalence-matched slice** separate from the balanced one
- **Cascade baseline**, a cheap filter plus an existing model, at matched cost. This is the baseline that can kill the project, so it goes in early rather than late.

## 10. Go or no go

Proceed past phase 2 only if all four hold:

1. The bag-size-conditioned aggregator stays calibrated as N grows by two orders of magnitude. If ECE degrades monotonically with N and conditioning does not fix it, the central technical claim is dead and you have spent $30 finding out.
2. Localisation is usable, not just the bit. Precision@5 well above the chunk base rate.
3. The cascade baseline does not already match you at equal cost.
4. Injected-to-real transfer holds. If accuracy collapses from synthetic injections to the real-incident set, fix the data before training anything larger.

A negative result on 1 or 3 is publishable and cheap. That asymmetry is the best argument for running the pilot: the downside is a few hundred dollars and a short honest paper, and the upside is a model class nobody currently sells.
