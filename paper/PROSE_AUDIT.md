# Prose audit: the AI tells in this draft, and what each becomes

Audited 27 September 2026 against `latex/main.tex` and `latex/section_typed.tex`. The pattern flagged is **unearned antithesis**: defining something by what it is not, when the negated half carries no information. It reads as machine-generated because a model uses the frame to sound decisive without adding a claim.

House rule going in: keep a contrast only when the reader would plausibly believe the wrong half. `X, not Y` earns its place when Y is a real and tempting alternative. It does not when Y is a straw man nobody proposed.

## The counts

| Pattern | Instances | Keep | Cut or rewrite |
|---|---:|---:|---:|
| `rather than` | 24 | 6 | 18 |
| `X, not Y` | 10 | 3 | 7 |
| `is not a ...` | 4 | 2 | 2 |
| `not just ...` | 2 | 0 | 2 |
| emphasis adverbs (`exactly`, `deliberately`, `actually`, `entirely`) | 7 | 3 | 4 |
| Total | 47 | 14 | 33 |

## Cut: the negated half adds nothing

These are the clearest cases. In each the alternative was never in contention.

| Where | Current | Becomes |
|---|---|---|
| Abstract | "marketed on latency and calibration rather than on reasoning" | "marketed on latency and calibration" |
| §1 | "The output is a distribution rather than a string, so calibration is..." | "The output is a distribution, so calibration is..." |
| §1 | "reading the probabilities of the allowed labels rather than generating and reparsing prose" | keep — generative parsing is the real alternative a reader assumes |
| §4.1 | "Row counts were measured from the downloaded files rather than taken from dataset cards" | keep — card counts genuinely disagree with ours, so the contrast is the claim |
| §6.1 | "measures a coherent capability rather than an artefact of our prompt wording" | "is evidence that the harness measures a coherent capability" |
| §6.4 | "a budget difference rather than a capability difference" | keep — this is the paper's actual ambiguity |
| §6.5 | "report this count rather than clipping it away" | "report this count; clipping it away hides an infinite average" |
| §7 | "publish a recommended operating point rather than leaving integrators to assume 0.5" | "publish a recommended operating point, since integrators otherwise assume 0.5" |
| §7 | "evaluate on their own decision shape rather than on an aggregate score" | "evaluate on their own decision shape" |
| §9 | "read from the released artifacts rather than transcribed" | "read from the released artifacts" |
| §2.1 | "the full vector, not just the argmax, which is what makes calibration measurable at all" | "the full vector, which is what makes calibration measurable" |
| §2.2 | "one forward pass regardless of K, rather than one pass per candidate token" | keep — this is a quantitative comparison, not a rhetorical one |
| §2.2 | "a model that reads the question rather than the layout" | keep — the layout-reading failure is exactly what we measure |
| §8 | "so this is inspectable rather than assumed" | "so this is inspectable" |
| §6.3 title | "must be measured, not assumed" | "Context budget is a confound" |

## Rewrite: antithesis doing real work but stated as a slogan

These carry a claim. The claim stays; the slogan framing goes.

| Where | Current | Becomes |
|---|---|---|
| §7 | "**Calibration, not accuracy, is the binding constraint.** The largest single improvement ... is not a better model but a better threshold" | "**Calibration is the binding constraint.** The largest single improvement available to any model in this study comes from moving the threshold, not from changing model" — one contrast, kept, because "buy a better model" is the reflex it corrects |
| §7 | "this is an operational finding, not a scoring technicality" | "this changes which actions a deployed gate takes" — states the consequence instead of denying a label |
| §6.1 | "**The exception is informative.**" | "**One slice reverses the ordering.**" — says what happened |
| §2.2 | "It is a property of the output distribution and carries no calibration guarantee" | keep — the guarantee is what a reader would wrongly assume |

## Emphasis adverbs to drop

`exactly` ×4 (two are load-bearing: "exactly its context limit", "exactly that"), `deliberately` ×1, `actually` ×1, `entirely` ×1. Cut the four that only add heat.

## Two patterns absent, checked and confirmed

No em dashes anywhere (house style). No two-sentence "It is not X. It is Y." constructions.

## What stays and why

Fourteen contrasts survive. Each names an alternative a reader would otherwise assume: generative parsing as the interface, dataset-card counts as the row source, context budget versus capability, layout versus question, threshold versus model quality. Those are the paper's arguments, and stating them as contrasts is how the argument works.
