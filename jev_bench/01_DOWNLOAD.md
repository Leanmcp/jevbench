# jev-bench step 2: download and verify

Written 26 September 2026. This step downloads nothing until you run it, and it never calls a model or an API that costs money.

- [sources.json](sources.json) is the pinned manifest: 12 sources, each with a commit sha, exact file paths, real column names, the gold field, the hidden fields and the model-visible allowlist.
- [workspace/download.py](workspace/download.py) fetches those files at those shas and measures what arrived.
- `data/MANIFEST.measured.json` is the output: byte sizes, sha256, row counts, observed columns, label distributions.

Every revision, path, column name and label vocabulary in `sources.json` was read live from the Hugging Face dataset API and datasets-server on 26 September 2026. Row counts are deliberately absent from it; the script measures them, so no count in this repo is a remembered number.

## Run it

```bash
cd /Users/ddod/LEANMCP/JEV_RELATED/jev_bench
uv sync
uv run workspace/download.py --list
```

`uv sync` resolves `huggingface-hub` and `pyarrow` to their current published versions and writes `uv.lock`. `--list` prints the plan and exits, which also catches any syntax error before anything downloads.

Then the text sources, which are small:

```bash
time uv run workspace/download.py --skip scienceqa --skip vqa_rad
```

Then the multimodal pair separately, because ScienceQA's test parquet alone is about 122 MB:

```bash
time uv run workspace/download.py --only vqa_rad --only scienceqa
```

Re-running is cheap: the Hub cache means unchanged files are not refetched, and the script merges new measurements into the existing manifest rather than discarding sources it did not select.

## What to read in the output

| Check | Why it matters |
|---|---|
| `WARNING columns in manifest but not in file` | The upstream schema moved. The adapter in step 3 is built from these column names, so fix `sources.json` before proceeding. |
| `WARNING expected 77 classes, observed N` | BANKING77 must have exactly 77 intents. If it does not, the option-count stress slice is not what it claims. |
| `gold field ...: N distinct, M null` | Aegis has null `response_label` on many rows, and any unexpected nulls elsewhere mean the gold field is wrong. |
| Row counts | Measured from the downloaded files; these are the counts used everywhere else. |
| `label_distribution.counts` | Feeds stratified sampling in step 3. Do not sample 500 rows uniformly from BANKING77 and expect all 77 intents. |

## Approximate download sizes

Measured by HTTP HEAD on 26 September 2026, for the single pinned file per source:

| Source | Bytes |
|---|---:|
| prompt_injections | 10,892 |
| sst5 | 342,783 |
| jailbreak_classification | 453,350 |
| pubmedqa | 1,075,513 |
| medmcqa | 1,476,104 |
| aegis2 | 1,731,373 |
| medqa_usmle | 2,075,679 |
| mmlu_pro | 4,144,185 |
| atbench500 | 5,422,164 |
| vqa_rad | 10,312,735 |
| scienceqa | 122,386,007 |
| banking77 | not measured, small |

Roughly 150 MB total, dominated by ScienceQA. The Hub cache stores a second copy alongside the `data/<key>/` copy, so budget about twice that on disk.

## Two things that changed from step 1

**BANKING77 substitution.** `PolyAI/banking77` and `legacy-datasets/banking77` are loading-script datasets: the repo contains `banking77.py` and no parquet, and current `datasets` releases will not execute that without remote code. The manifest uses `mteb/banking77`, which carries the same upstream test split as parquet plus a `label_text` column, so the 77 intent names come from the data rather than from anyone's memory. The data is still PolyAI's CC-BY-4.0 corpus and PolyAI is what you cite.

**SST-5 is not redistributable as text.** Its card states no license. It is marked `redistributable: false` in the manifest, which means the published release carries its `case_id`, source row index and a content hash, and a script rebuilds the text locally. Same treatment applies to any other source whose card stays silent.

## Leakage guards now encoded in the manifest

Each source lists `model_visible` and `hidden`. Step 3's adapter reads only `model_visible`. The fields worth naming explicitly, because each is a plausible accident:

- `medmcqa.exp`, `mmlu_pro.cot_content`, `pubmedqa.long_answer`, `scienceqa.lecture`, `scienceqa.solution` are gold rationales.
- `atbench500.risk_source`, `atbench500.failure_mode`, `atbench500.real_world_harm` and `aegis2.violated_categories` are gold-adjacent annotations that all but announce the label.
- `medqa_usmle.answer` is the gold option text, so it leaks even though it is not the letter.

`prompt_injections`, `jailbreak_classification`, `aegis2` and `atbench500` contain adversarial text by construction. It is state, it is data, and the adapter wraps it as untrusted. The download script prints no record content for exactly this reason.

## Next

Step 3: the adapter and runner. One adapter per task type (`noul`, `choice`, `score`) reading the `model_visible` allowlist, stratified sampling to `target_n`, then Jev through `api.typesafe.ai` and djev through the A100, logging full probability vectors into the `predictions` table.
