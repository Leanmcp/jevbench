# Quick benchmark

A small smoke test used before the main JevBench runs. It is not part of the
paper's results.

## `data/jevbench_easy_48.jsonl`

48 typed-decision cases from the public easy tier of Benchmark Heaven's JevBench
([fstandhartinger/jevbench](https://github.com/fstandhartinger/jevbench), commit
`1bcc55eb6c8cffde2306b3db03ede39b61c6152a`), an independent project that shares
this repository's name. The file is redistributed under that project's MIT
Licence; its copyright notice is in
[`data/LICENSE-fstandhartinger-jevbench`](data/LICENSE-fstandhartinger-jevbench).

Each row includes `expected` answers and provenance. Send only the task state and
question to a model, never the whole row. A score on this subset is not
comparable with Benchmark Heaven's official JevBench score.

## R-Judge

An earlier version of this folder carried 50 records from
[R-Judge](https://github.com/Lordog/R-Judge). R-Judge publishes no licence, so
its records are not redistributed here. To reproduce that smoke test, clone
R-Judge at commit `83ce301da3ad50dd8b397e772863f5411c3d3dc2` and, within each of
its five categories (Application, Finance, IoT, Program, Web) and each label,
take the first five records by numeric ID.
