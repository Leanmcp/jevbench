# MCPMark and MCP-Bench on Jev and Liquid D1

This integration evaluates **offline typed decisions** using the existing Jev
and Liquid D1 clients. It does not run an autonomous agent, execute MCP tools,
or reproduce either upstream benchmark's end-to-end leaderboard.

Both complete Git repositories are downloaded, including task specifications,
verifiers and bundled code. Remote environment snapshots and live service data
are not downloaded or initialized. No upstream installer or server is executed.

## Sources and scope

Exact Git commits, source URLs and licence findings are in `mcp_sources.json`.
The downloader checks out those commits and refuses to modify a dirty checkout.

- [MCPMark](https://github.com/eval-sys/mcpmark), paper
  [2509.24002](https://arxiv.org/abs/2509.24002): the pinned repository contains
  127 standard tasks (MCPMark Verified) and 50 easy tasks. Its official outcome
  is verified task completion, not a universal next-tool label.
- [MCP-Bench](https://github.com/Accenture/mcp-bench), paper
  [2508.20453](https://arxiv.org/abs/2508.20453): all 104 released tasks are
  downloaded, including single-, two- and three-server tasks. The task plans
  and dependency analyses are withheld from model input. A plan can have
  multiple valid execution orders, so its first mentioned tool is not treated
  as unique next-tool gold.

| Slice | Base cases | Parent tasks | Measures |
|---|---:|---:|---|
| `mcpmark_server_routing` | 127 | 127 | Associated server environment, using `meta.description` |
| `mcpbench_server_routing` | 56 | 56 | Associated server, using `fuzzy_description` |
| `mcpmark_tool_selection` | 9 | 3 | Authored checkpoints in filesystem tasks |
| `mcpbench_tool_selection` | 13 | 4 | Authored checkpoints in API, Wikipedia, Hub and paper-search tasks |

There are 205 base decisions, or 410 with reordered twins. MCPMark routing
uses the six environment directory labels, including `playwright_webarena` as
separate from `playwright`. MCP-Bench routing uses all 28 single-server labels
as candidates. Git-tracked metadata defines the MCPMark task inventory; the
`insforge` and `supabase` symlinks to `postgres` are excluded as duplicate aliases.
Multi-server tasks are downloaded but excluded from this
single-label routing metric. Server names can be explicit in task text, so
routing is a diagnostic rather than a difficult tool-use score.

**Tool-selection accuracy** means the fraction of checkpoints where the model
selects the annotated function among the supplied candidates. Checkpoints and
short tool descriptions were authored for JevBench; they are not official gold
trajectories or real execution traces. A checkpoint supplies hypothetical
progress, such as “the largest JPEG is already identified; rename it now.”
The full task and checkpoint are model-visible. Gold, evidence and provenance
are withheld. Candidate catalogues are curated (5 filesystem functions or 13
cross-server functions), not the benchmarks' complete live inventories.

This is a small starter subset, not representative coverage of either full
benchmark. In particular, the MCPMark tool subset uses filesystem tasks only.
It tests choosing a function, not argument generation, live tool execution,
multi-step planning or final task success. Add reviewed checkpoints to
`annotations/mcp_tools.json` to expand it; keep ambiguous alternatives out of
single-gold questions. Do not manufacture gold labels from model predictions.

## Commands to run yourself

From the repository root:

```bash
cd jev_bench
bash scripts/20_download_mcp.sh
uv sync --locked
uv run workspace/test_mcp.py
uv run workspace/build_mcp_cases.py --permute
bash scripts/42_run_mcp.sh dry-run jev
bash scripts/42_run_mcp.sh dry-run liquid
```

The test is offline; it checks pinned coverage, option permutations, scoring,
model-visible fields and Jev/D1 request parity. The wrapper runs verification
before every evaluation. Verification reconstructs cases from the clean pinned
checkouts and annotation file and rejects edited/stale cases. Long task states
fail rather than being silently truncated. No new Python dependencies are added.

Set `TYPESAFE_API_KEY` and `LIQUID_API_KEY` securely in your shell using your
existing credentials. Keys are read by the existing clients, not stored by
these scripts. Then run the smoke trials:

```bash
bash scripts/42_run_mcp.sh trial jev
bash scripts/42_run_mcp.sh trial liquid
```

Each trial sends up to three decisions per slice. Inspect its report and
coverage before running both complete **derived slices**:

```bash
bash scripts/42_run_mcp.sh full jev
bash scripts/42_run_mcp.sh full liquid
uv run workspace/paired_bootstrap.py \
  --runs Jev=mcp-v1-jev-full --runs D1=mcp-v1-liquid-full
```

Models default to the existing `jev-1.13.0` and `d1:free` configuration.
`MCP_CONCURRENCY=1` lowers concurrency. `MCP_RUN_ID=your-new-run-id` selects a
new run; otherwise rerunning resumes the same run. Use a new ID after changing
cases or annotations; the runner rejects a changed MCP case fingerprint.
Do not run two writers against the same ID.

If a provider errors, the wrapper stops without proceeding to comparison.
You may still score its partial run explicitly:

```bash
uv run workspace/score_runs.py --run-id mcp-v1-liquid-full
uv run workspace/report.py --run-id mcp-v1-liquid-full
```

## Artifacts and interpretation

- `data/upstream/{mcpmark,mcpbench}/`: pinned full repository checkouts.
- `data/cases/mcp*.jsonl`: exact inputs, withheld labels and provenance.
- `data/mcp_build_manifest.json`: counts, distributions and SHA-256 file hashes.
- `data/runs/<run-id>/`: predictions, metadata and scores.
- `reports/RESULTS_<run-id>.md`: readable report.

Scores name `tool_selection_accuracy` and `server_routing_accuracy` separately.
Existing accuracy, macro-F1, Brier, calibration, probability and latency metrics
remain available. Headlines condition on valid returned decisions. MCP scores
also provide `accuracy_counting_recorded_errors_as_wrong` and
`accuracy_over_planned_cases`, plus missing-prediction counts. Report coverage
alongside every score. A fully absent slice has no score entry; compare the
reported slices with the four expected slices above.

All checkpoints and option permutations from one source task share `family_id`.
Bootstrap uncertainty is therefore grouped by task. The tool slices have only
three or four independent task families, so the current scorer intentionally
omits their individual confidence intervals. Reordered twins do not increase
independent sample size. The paired comparison may omit small slices.

Keep these scores separate from the existing published benchmark results and
from official MCPMark/MCP-Bench success rates. No new measured results have been
produced by this change. Hosted model aliases may change over time; retain run
timestamps and the reported model version.

MCPMark has an Apache-2.0 root licence. No root task licence was found in the
pinned MCP-Bench checkout; derived MCP-Bench rows are conservatively marked
`redistributable: false`. Local source/case downloads are gitignored. Bundled
server licences do not establish a licence for the task collection.
