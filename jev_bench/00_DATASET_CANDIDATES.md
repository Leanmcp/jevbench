# jev-bench: dataset candidates (step 1 of 3)

Drafted 26 September 2026. Nothing has been downloaded or run yet. Licenses, gating and repo existence in the tables below were read live from the Hugging Face dataset API on this date. Row counts are deliberately **not** stated here: the download script in step 2 prints the authoritative counts from the files it fetches, so no number in this repo comes from memory.

Related: [benchmark research](../PRELIM_RESEARCH/02_benchmarks_and_evaluation.md) · [paper plan](../reports/Benchmark_and_paper_plan.md) · [local smoke sets](../quick_benchmark/README.md).

## What jev-bench is measuring

Jev and djev do not emit prose. They expose exactly three typed decisions ([djev API](../model_workspace/djev-source/docs/api.md), [Laya limits](../Laya_Architecture/Schema_and_limits.md)):

| Type | Output | Natural dataset shape |
|---|---|---|
| `noul` | one probability in [0,1] | binary labels, yes/no questions, safety verdicts |
| `choice` | named option + full probability vector | multiple choice, intent classes, topic labels |
| `score` | expected level index over an ordered rubric | star ratings, severity, 5-point sentiment |

So the benchmark axis is not "which subject is the question about". It is **decision shape**: how many options, how ordered, how grounded, how long the state, how many questions per state. A multiple-choice exam is one cell in that grid, and your instinct is right that it maps cleanly onto `choice`.

One thing to decide consciously before spending money. Two very different things get tested by MCQ data:

- **Knowledge recall.** "Which drug treats X" with no passage. The answer lives in the weights. A 421M or a 4B-active decision model will look bad here, and that is a statement about model size, not about decision quality.
- **Grounded decision.** The evidence is in the state and the model has to read it and pick. PubMedQA, BoolQ, R-Judge and your own authorization cases are this.

Both belong in the release, but they must be separate slices with separate headline numbers. A single blended "jev-bench score" that mixes them is not interpretable.

## About "AIMLE"

I could not resolve that name to a real dataset. The closest things matching "multiple choice plus diagnosis" are listed as C1 to C3 below. If you meant an Indian medical entrance corpus (AIIMS / NEET-PG style stems), that is **MedMCQA**, which is exactly the diagnosis-flavoured 4-option MCQ set you described, and it happens to be Apache-2.0, which matters for republishing. If AIMLE is an internal or private set, say so and it becomes a private slice instead.

## Tier 0: already on disk, use for wiring only

| Set | Local path | Shape | Why |
|---|---|---|---|
| JevBench easy public tier | `quick_benchmark/data/jevbench_easy_48.jsonl` | mixed typed decisions | Only set with published Jev numbers to sanity-check the adapter against |
| R-Judge subset | `quick_benchmark/data/inputs.json` | `noul`, safety | Already sampled 25/25, offline, zero cost |

These are smoke tests. Do not put them in a results table.

## Tier 1: multiple choice, the thing you asked for

| # | Dataset | Repo id | License | Options | Notes |
|---|---|---|---|---:|---|
| C1 | MedMCQA | `openlifescienceai/medmcqa` | apache-2.0 | 4 | Medical entrance MCQs, heavy diagnosis and pharmacology. Redistributable. **Recommended first run.** |
| C2 | MedQA (USMLE, 4-option) | `GBaker/MedQA-USMLE-4-options` | cc-by-4.0 | 4 | Longer clinical vignettes. Good length-stress contrast against C1's short stems. |
| C3 | MMLU | `cais/mmlu` | mit | 4 | 57 subjects, lets you report per-subject breakdown from one adapter. High contamination risk. |
| C4 | MMLU-Pro | `TIGER-Lab/MMLU-Pro` | mit | 10 | Same adapter, 10 options. This is your cheapest option-count ablation. |
| C5 | ARC | `allenai/ai2_arc` | cc-by-sa-4.0 | 4 | Easy/Challenge split gives a difficulty axis for free. |

All five are `choice` with one question per state. One adapter covers all of them, which is why this tier is the right place to start.

## Tier 2: option-count stress (2 / 4 / 10 / 60 / 77 / 150)

djev accepts 255 choice options per question; Laya accepts 100 but shrinks each option's description as the count grows. Whether large option sets actually work is an empirical question and one of the more publishable things here.

| # | Dataset | Repo id | License | Options |
|---|---|---|---|---:|
| C6 | BANKING77 | `PolyAI/banking77` | cc-by-4.0 | 77 |
| C7 | CLINC150 | `clinc/clinc_oos` | cc-by-3.0 | 150 (+ out-of-scope, tests abstention) |
| C8 | MASSIVE | `AmazonScience/massive` | cc-by-4.0 | 60, across 51 languages |

C7's out-of-scope class is the only public set here that directly tests "none of these", which is the abstention behaviour your paper plan cares about.

## Tier 3: ordinal, for the `score` type

| # | Dataset | Repo id | License | Levels |
|---|---|---|---|---:|
| C9 | SST-5 | `SetFit/sst5` | unspecified on card | 5 |
| C10 | Yelp review full | `Yelp/yelp_review_full` | other (check terms) | 5 |
| C11 | GoEmotions | `google-research-datasets/go_emotions` | apache-2.0 | 28, multi-label |

Report MAE and ranked probability score, not just exact accuracy. C11 is multi-label, so it is really a bank of 28 `noul` questions on one state, which doubles as your questions-per-state batching test.

## Tier 4: grounded binary and three-way, for `noul`

| # | Dataset | Repo id | License | Shape |
|---|---|---|---|---|
| C12 | BoolQ | `google/boolq` | cc-by-sa-3.0 | passage + yes/no |
| C13 | PubMedQA | `qiaojin/PubMedQA` | mit | abstract + yes/no/maybe |
| C14 | XNLI | `facebook/xnli` | unspecified on card (CC-BY-NC in upstream paper, verify) | 3-way, 15 languages |

C13 is the best of the medical candidates for an honest evaluation: the evidence is supplied, so a small model is not being punished for not memorising medicine, and "maybe" is a real abstention class.

## Tier 5: safety and guard decisions, closest to Jev's actual product

| # | Dataset | Repo id | License | Notes |
|---|---|---|---|---|
| C15 | ATBench | `AI45Research/ATBench` | apache-2.0 | Agent trajectory safe/unsafe. Already scoped in `quick_benchmark`. |
| C16 | Aegis 2.0 | `nvidia/Aegis-AI-Content-Safety-Dataset-2.0` | cc-by-4.0 | Content safety with a taxonomy, so both `noul` and `choice` |
| C17 | prompt-injections | `deepset/prompt-injections` | apache-2.0 | Small, cheap, directly relevant to the gateway |
| C18 | jailbreak-classification | `jackhhao/jailbreak-classification` | apache-2.0 | Same |
| C19 | WildGuardMix | `allenai/wildguardmix` | odc-by, **gated (auto)** | Needs an accepted licence on your HF account before download |
| C20 | ToxicChat | `lmsys/toxic-chat` | cc-by-**nc**-4.0 | Non-commercial. Usable for research, do not redistribute inside a permissive release. |

## Tier 6: multimodal, djev only

djev takes one state image and up to six image attachments per request, including **images as options**. Nothing in the published Jev comparisons exercises that, so it is genuinely open ground.

| # | Dataset | Repo id | License | Notes |
|---|---|---|---|---|
| C21 | VQA-RAD | `flaviagiammarino/vqa-rad` | cc0-1.0 | Radiology, closed-form yes/no plus categories. CC0 means you can republish the adapted slice. |
| C22 | PathVQA | `flaviagiammarino/path-vqa` | mit | Pathology images |
| C23 | ScienceQA | `derek-thomas/ScienceQA` | cc-by-sa-4.0 | MCQ with and without images, so one dataset gives a text-vs-image ablation |

## Tier 7: your own contribution

The authorization/policy cases from `reports/Benchmark_and_paper_plan.md` section 3. No public set covers policy-shift, authorization provenance or missing-evidence escalation. That is the part of jev-bench that is yours, that nobody can be contaminated on, and that a paper can be built around. Everything in tiers 1 to 6 is context for it.

## Contamination flags to carry as a column

Not a footnote. A column in the dataset.

- Laya reports AG News and BoolQ in its training mixture.
- Together's recipe reports MultiNLI, BoolQ, BANKING77, AG News and SST-5.
- MMLU, ARC and SST-2 are near-certainly in the pretraining of any base model involved, DiffusionGemma included.
- MedMCQA, MMLU-Pro, CLINC150, VQA-RAD and PathVQA have no reported exposure in these specific mixtures, which is not the same as being clean.

Held-out records from an exposed task measure in-domain generalisation, not transfer. Mark each row `exposure: reported | likely | unknown` and never aggregate across that flag without saying so.

## Publishing shape: two configs, not one table

The "giant database" should be two Hugging Face configs plus a card.

**`cases`** is one row per decision, identical schema across every tier:

```
case_id, family_id, source, source_revision, source_split, license, exposure,
task_type (noul|choice|score), capability (binary|mcq_small|mcq_large|ordinal|grounded|safety|multimodal|multilingual),
state (JSON, model-visible fields only), question (instructions + criteria), n_options, option_order_seed,
perturbation (none|permuted|opaque_labels|distractor|negation),
gold, gold_index, est_input_tokens
```

**`predictions`** is one row per (case, model, seed), which is what makes the release reusable:

```
case_id, model, model_version, endpoint, seed, samples,
raw_response (probabilities for every option), pred, correct,
latency_ms, input_tokens, output_tokens, error, run_id, run_timestamp
```

Everyone publishes the cases and throws away the probabilities. Publishing the full probability vectors is what lets other people compute calibration, risk-coverage and KL against soft references without re-running anything, and it costs you nothing because you already have the numbers.

Two hard constraints on redistribution:

1. Licenses do not merge. A single Apache-2.0 release containing ToxicChat (NC) and a card-unspecified set is not defensible. Either ship one config per source with its own license field and a per-source terms table, or ship only the permissive sources (C1, C4, C6, C7, C8, C11, C13, C15, C16, C17, C18, C21, C22) as text, and for the rest ship `case_id` + source row index + a content hash so a script can rebuild them locally.
2. Gold labels, risk categories and provenance metadata must sit outside the `state` field. The adapter builds model input from an explicit allowlist, as your paper plan already specifies. This is the single most common way a benchmark quietly breaks.

## Recommended v0.1 scope

Small enough to finish, broad enough to be a real result.

| Slice | Set | Cases | Why |
|---|---|---:|---|
| MCQ, knowledge | C1 MedMCQA | 500 | Your diagnosis MCQ ask, redistributable |
| MCQ, options=10 | C4 MMLU-Pro | 500 | Option-count contrast, same adapter |
| MCQ, options=77 | C6 BANKING77 | 500 | Matches the one published Jev MCQ-ish comparison, so your numbers are checkable |
| Grounded 3-way | C13 PubMedQA | 500 | Medical but fair, plus an abstention class |
| Ordinal | C9 SST-5 | 500 | Exercises `score` |
| Safety | C15 ATBench500 | 500 | Product-relevant, already scoped |

3,000 decisions, one adapter per task type, 500 per set to match the sample size the existing public Jev runs used. Add the option-permutation perturbation to MedMCQA and BANKING77 from day one: it is free, it doubles those slices, and position bias in a `choice` model is a finding.

## Next steps

Step 2: download scripts, one per chosen set, writing to `jev_bench/data/<source>/`, printing exact row counts, file sizes and checksums so the numbers in this document get replaced by measured ones. Step 3: the adapter plus runner, Jev through `api.typesafe.ai` and djev through the A100, same cases, logged probabilities.
