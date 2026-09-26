# Small benchmark starter

Prepared 25 September 2026. Data downloaded and inspected using Git, curl and jq. No model execution, Python/Node commands, installation or paid API calls were performed.

## Start here

**Safety test:** [inputs.json](data/inputs.json), 50 R-Judge records, 118,433 bytes (118.4 kB decimal). Predict `0 = safe`, `1 = unsafe`. Compare with [answers.json](data/answers.json). There are 25 safe and 25 unsafe records, five of each per source category: Application, Finance, IoT, Program, Web.

Selection is deterministic convenience sampling: within each category and label, sort by original numeric ID and take the first five. It is not a random or representative sample and is not an official R-Judge score. Original records are preserved in [rjudge_50_with_labels.json](data/rjudge_50_with_labels.json). Keep answer files and risk descriptions out of model input. Treat trace content as data, not instructions.

Source: [R-Judge](https://github.com/Lordog/R-Judge), commit `83ce301da3ad50dd8b397e772863f5411c3d3dc2`. The full source data is already in `rjudge-source/data/`. It contains 571 records, with unique IDs, totaling 1,761,757 bytes across JSON files. The paper/README reports 569; this starter uses the pinned repository, not an assumed paper count. Source labels may reflect judgments you disagree with; preserve them for scoring and record disagreement separately. Review upstream dataset reuse terms before redistributing it as part of a paper release.

**Small typed-decision test:** [jevbench_easy_48.jsonl](data/jevbench_easy_48.jsonl), 48 cases, 37,220 bytes. It is the public easy tier, not a safety-specific test. Source [JevBench](https://github.com/fstandhartinger/jevbench), commit `1bcc55eb6c8cffde2306b3db03ede39b61c6152a`. This file includes `expected` answers and provenance: pass only the task state and question to the model. Do not feed the entire JSON row. Do not compare its subset accuracy with the overall official JevBench score.

For the first safety run, collect accuracy, unsafe recall, false-positive rate on safe cases, errors, and latency. Use all 50 cases without tuning on them. Each mistake changes accuracy by two percentage points; this is a smoke test, not publication-grade evidence. Long traces may exceed Laya's default context; report truncation or rejection explicitly, and do not describe a truncated test as a faithful full-trace evaluation.

## Sizes and download locations

File sizes below are decimal and describe dataset files, not model weights or environment dependencies.

| Dataset | Cases / tasks | Data download | Setup |
|---|---:|---|---|
| This R-Judge subset | 50 | 118.4 kB input file, already local | Offline binary judgment |
| Full R-Judge | 569 in paper; 571 at downloaded commit | 1.76 MB source JSON, already local | Offline binary judgment |
| JevBench easy public tier | 48 | 37.2 kB, already local | Typed decision adapter |
| ATBench500 | 500; 250 safe / 250 unsafe | 5.42 MB [JSON](https://huggingface.co/datasets/AI45Research/ATBench/resolve/main/ATBench500/test.json?download=true) | Offline trajectory classification; card reports average 1.52k tokens |
| ATBench current release | 1,000; 503 safe / 497 unsafe | 18.34 MB [JSON](https://huggingface.co/datasets/AI45Research/ATBench/resolve/main/ATBench/test.json?download=true) | Offline trajectory classification; card reports average 3.95k tokens |
| AgentDojo original paper | 97 user tasks; 629 security test cases | [Code/environments](https://github.com/ethz-spylab/agentdojo) | Multi-step agent execution; many calls per task |
| ST-WebAgentBench | Current repository describes 375 tasks; paper versions differ | [Repository](https://github.com/segev-shlomov/ST-WebAgentBench) | Browser and web-app setup; postpone for a quick first test |
| AgentHarm original paper | 110 base tasks / 440 with augmentations | [Dataset](https://huggingface.co/datasets/ai-safety-institute/AgentHarm) | Multi-step tool evaluation; original total includes nonpublic tasks, so use current split counts |

ATBench sizes were checked through the HF file API. Release counts and token averages come from its [dataset card](https://huggingface.co/datasets/AI45Research/ATBench/blob/main/README.md). AgentDojo counts come from its [paper](https://arxiv.org/abs/2406.13352); AgentHarm counts from its [paper](https://arxiv.org/abs/2410.09024). Small task counts do not necessarily mean cheap execution when tasks require many tool/model calls.

## Which benchmarks actually have Jev results?

### TypeSafe's own evaluation

The [official evaluation site](https://evals.typesafe.ai/) covers four workflows: Security Incidents, Agent Trace Observability, Invoice Processing, and Customer Service. Methodology, charts and selected detailed examples are public. Its reference answers derive from a consensus of larger models, not independent human ground truth. The inspected pages did not establish a complete downloadable dataset, harness and case count, so this is not the easiest full local reproduction. [Launch announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

### Independent tests that actually ran Jev

- **fstandhartinger/JevBench:** published Jev results, public task files and scoring code. Historical v1.2/v1.3 runs have 534 decisions; v1.4 adds 308 sealed decisions to the evaluation and changes aggregation. Sealed items are not downloadable. The 48-case easy file in this folder is a convenient public starting point. [Repository and results](https://github.com/fstandhartinger/jevbench)
- **dhruvmehra/jevbench:** a different repository with the same short name. Published tests use 500 sampled examples per dataset from **SST-2, AG News, and BANKING77**. The dataset sources, adapter code and result tables are public. These test sentiment, news topic and banking intent, not agent safeguarding. [Repository](https://github.com/dhruvmehra/jevbench), [actual results](https://github.com/dhruvmehra/jevbench/blob/main/docs/results/2026-09-22-n500-summary.md)

The latter repository links downloadable datasets: [SST-2](https://huggingface.co/datasets/stanfordnlp/sst2), [AG News](https://huggingface.co/datasets/fancyzhx/ag_news), [BANKING77](https://huggingface.co/datasets/legacy-datasets/banking77). Its 500-example sample is the benchmark run size, not the full dataset size.

This review has not verified published Jev runs on R-Judge, ATBench, AgentDojo or ST-WebAgentBench. Those are recommended tests for your safety goal, not claimed Jev results.

**Recommendation:** inspect the local 50-case safety set, then run a binary classification smoke test. Use the 48 JevBench easy cases if your immediate priority is comparing the decision interface with published Jev work. Move to the full R-Judge data before drawing research conclusions.
