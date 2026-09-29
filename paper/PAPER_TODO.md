# Paper TODO

Status of [latex/main.tex](latex/main.tex) (11 pages, builds clean) and the mirror at [jevbench_preprint.md](jevbench_preprint.md). Updated 27 September 2026.

Authors: Dheeraj Mohandas Pai (dheeraj.pai@leanmcp.com), Lu Xian (lu.xian@leanmcp.com), LeanMCP.

## Done

| # | Item | Where |
|---|---|---|
| T1 | Typed decisions defined, with three worked examples using real probabilities from our runs, plus the simplex formalism, label-restricted read, calibration and order-invariance definitions | `latex/section_typed.tex`, §2 |
| T2 | RLCD defined and correctly attributed | `latex/section_related.tex`, §3.1 |
| T3 | Related work rewritten: four subsections with 18 real citations, including the constrained-decoding comparison that was entirely absent | `latex/section_related.tex` |
| T4 | Opacity limitation for the commercial model | `main.tex`, §8 |
| — | Author block and affiliations | `main.tex` |
| — | `references.bib`: 19 entries, each tagged with how it was sourced | `latex/references.bib` |
| — | Prose de-AI pass: 33 of 47 unearned-antithesis constructions removed | [PROSE_AUDIT.md](PROSE_AUDIT.md) |

**Correction carried out of the old version of this file:** RLCD expands to Reinforcement Learning from **Contrast** Distillation, not "Contrastive Distillation". The old draft here had it wrong. Verified against arXiv:2307.12950 and the `facebookresearch/RLCD` repository.

## Blocking submission

**B1. Verify the seven `[memory]` bibliography entries.** `references.bib` tags every entry with its provenance: `[card]` means the BibTeX came verbatim from the dataset's own Hugging Face card, `[search]` means venue and identifier were confirmed against arXiv, ACL Anthology or PMLR, and `[memory]` means the reference is canonical but the author list and page numbers have not been checked. The `[memory]` entries are socher2013sst, guo2017calibration, naeini2015ece, brier1950, gneiting2007scoring, kwon2023vllm. Check each against the primary source before submission. None was invented, but none of those six is confirmed either.

**B2. Two `\draftnote` markers remain.** `build.sh` counts them on every build and they must reach zero: the archival DOI in §9, and the AI-assistance wording in §10, which needs adapting to the target venue's current policy.

**B3. Paired bootstrap on shared case identifiers.** Table 2 reports unpaired intervals. All three models answered byte-identical cases, so the paired test is available and strictly stronger. Computable from the released predictions with no model re-runs. This is the highest value per unit of work on the list, and the first thing a reviewer will ask for.

**B4. Check the vendor's API terms of service** for any restriction on publishing benchmark results. The paper's central table names a commercial product.

## Strengthening, in descending value

**S1. Encoder-classifier baseline on BANKING77.** Without it, a reviewer can observe that a fine-tuned per-task classifier plausibly beats all three systems on the slice where they look most impressive. §3.1 already concedes the gap in writing, which makes the omission visible; filling it is better.

**S2. Reliability diagrams** for the three models on two representative slices. The threshold finding is the paper's headline and currently arrives as a table.

**S3. Risk-coverage curves.** The operationally meaningful form of the calibration result for a gate that can abstain.

**S4. Laya's `typed-decisions` checkpoint at 1,024 tokens.** Reporting only the 512-token English checkpoint as "Laya" is the most obvious methodological objection available, since a better-suited checkpoint ships in the same package.

**S5. `samples=4` on djev**, to test whether multi-read averaging improves calibration. Its API supports it; every run used 1.

**S6. MMLU-Pro restricted to four options**, gold retained, to separate option starvation from capability.

## The CLM question, unresolved

CLM-v0.1-8B \citep{kwok2026clm} was evaluated and is **not in the paper**, deliberately. Two full reruns agree to three decimal places and the harness is faithful (single-shot matches batch), but ATBench AUROC is 0.475 and vqa\_rad 0.502, which is coin-flip ranking, while the model answers its own documented examples at 0.99. Reproducible is not the same as correct. `jev_bench/workspace/probe_clm_options.py` sweeps candidate-set size from 2 to 77 and is the outstanding diagnostic; it needs the GPU up for about a minute. Until it runs, no CLM number should appear anywhere.

If the sweep shows accuracy collapsing with candidate count, that is a publishable finding about dual-encoder retrieval at scale and belongs in the paper as such. If it shows the numbers are an artefact of our request construction, CLM stays out and §3.3 gains a sentence about interface-level incompatibility between implementations of the same wire schema.

## Artifact mechanics

- Exclude the six trial runs from any release: `djev-trial`, `djev-imgtest`, `djev-parsetest`, `laya-en-trial`, and the two short Jev runs.
- Fix the leak-check causality inversion in `jev_bench/workspace/verify_cases.py`. The correct check is that every state field is derivable from the allowlist, not that no hidden field appears in the state. The current direction produced 33 false positives on ScienceQA, documented in §4.2.
- The throughput figures in §6.6 are client-concurrency artefacts, not model properties: the djev run used concurrency 6 and CLM later reached 34 requests/s at concurrency 24 on the same hardware. Only per-request p50 latency is comparable across systems. §6.6 needs a sentence saying so.
