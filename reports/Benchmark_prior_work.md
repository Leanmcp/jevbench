# Benchmarks and prior work for a trainable decision gate

Checked 25 September 2026. This is a targeted literature and repository review, not a systematic review or an experimental result. No benchmark has been executed. Companion: [proposed benchmark and paper](Benchmark_and_paper_plan.md).

## Which benchmarks to run first

Start with **R-Judge and ATBench for offline safety judgments, followed by AgentDojo for live intervention**. Add JevBench for typed-decision behavior. Use ST-WebAgentBench if enterprise policy compliance becomes the main paper claim. These measure different things; publish separate results rather than averaging their scores into one “safety score.”

| Priority | Benchmark | What it measures | How your model participates | Important limitation |
|---|---|---|---|---|
| 1 | R-Judge | Safety-risk recognition from recorded agent interactions | Read the record and predict its original safety label | Retrospective recognition does not establish prevention |
| 1 | ATBench | Agent-trajectory safety/security and risk diagnosis | Classify traces; optionally predict the published taxonomy | Full traces can reveal consequences unavailable before an action |
| 2 | AgentDojo | Prompt-injection attacks and defenses during tool-using tasks | Insert your gate before tool execution while keeping the underlying agent fixed | Results depend on agent, attacker, tools and integration, not only guard weights |
| 2 | JevBench | Typed-decision model behavior under its suite | Adapt each model to the same questions and allowed options | Not a complete agent-security evaluation |
| 3 | ST-WebAgentBench | Enterprise web-task completion subject to policies | Gate proposed browser actions; score resulting workflows | More environment setup; action context may include browser observations your text model cannot directly consume |
| 3 | AgentHarm | Execution of explicitly harmful multi-step requests, with benign comparisons available | Guard the tool path of the same agent on harmful and benign tasks | Malicious user requests differ from indirect injection into an authorized task |

### R-Judge: the cheapest useful starting point

The paper describes 569 multi-turn interaction records, 27 risk scenarios, five application categories and ten risk types. It supplies safety labels and risk descriptions. It is directly relevant to testing whether a model can recognize risk in context. Use its native task before introducing a new three-way label mapping. [Paper](https://arxiv.org/abs/2401.10019), [official repository](https://github.com/Lordog/R-Judge)

For the first run, report confusion matrix, macro-F1, balanced accuracy and class prevalence. Include constant predictions so a majority-class shortcut is visible. Do not infer an “escalate” ground truth from a binary label. Any prefix-only or three-way adaptation requires new annotation and a separately named result.

### ATBench and AgentDoG: the closest model competitor

AgentDoG introduces ATBench and a taxonomy organized around risk source, failure mode and consequence. Its original paper releases guard models in 4B, 7B and 8B variants. This is direct prior work for an open agent-safety monitor, not merely a generic moderation baseline. The repository has evolved, so freeze the benchmark release and checkpoint being compared. [Paper](https://arxiv.org/abs/2601.18491), [official code and release links](https://github.com/AI45Lab/AgentDoG)

Use an AgentDoG checkpoint as a strong open baseline where the task and input format fit. Audit whether evaluated examples appear in its training data. If overlap is unknown, disclose that limitation and use your independently held-out suite for the main generalization claim.

### AgentDojo: does the gate actually prevent the outcome?

AgentDojo evaluates attacks and defenses for agents that use tools over untrusted data. Its NeurIPS 2024 paper and open implementation make it a useful anchor for an end-to-end security experiment. [Paper](https://arxiv.org/abs/2406.13352), [repository](https://github.com/ethz-spylab/agentdojo)

Compare the same agent without your learned gate, with rules, and with each guard. Record legitimate-task success and attack success separately. Predetermine what happens after denial or escalation: stop, replan, or ask for review. A stopped task must not count as successfully completed merely because the attack failed.

### ST-WebAgentBench: policy compliance already has prior work

This benchmark extends web-agent evaluation with policies and measures Completion Under Policy alongside policy violations. It is highly relevant to the proposed customer-policy product. Its paper and current repository differ in scope and task inventory; use one pinned release and derive counts from that release rather than combining numbers. [Paper](https://arxiv.org/abs/2410.06703), [official repository](https://github.com/segev-shlomov/ST-WebAgentBench)

This rules out claiming that measuring useful task completion under policy is new. Your work could study a small, exportable guard and generalization to unseen authorization policies within that setting, but must establish what the new evaluation adds.

### AgentHarm: harmful requests with tool-use capability controls

The original paper describes 110 malicious base tasks, 440 including augmentations, across 11 harm categories. These are paper-design counts, not a promise that a current public evaluation runs all 440. Use the current release manifest for actual executed counts. The Inspect implementation exposes harmful and benign evaluations. [Paper](https://arxiv.org/abs/2410.09024), [official evaluation documentation](https://ukgovernmentbeis.github.io/inspect_evals/evals/agentharm/)

Useful when your service also addresses malicious users. Do not substitute it for testing whether retrieved content diverts a legitimate user task.

## Additional prior work that affects the paper

| Work | Why it matters to the proposed contribution |
|---|---|
| [Agent Security Bench / ASB](https://arxiv.org/abs/2410.02644), [code](https://github.com/agiresearch/ASB) | Broad agent attack/defense coverage, including memory and observation attacks. Use to expand threat coverage after a focused first experiment |
| [Agent-SafetyBench](https://github.com/thu-coai/Agent-SafetyBench) | Existing broader agent-safety evaluation. Inspect its environments and scoring before making any claim of comprehensive coverage |
| [AgentSpec](https://arxiv.org/abs/2503.18666) | Runtime rules with triggers, predicates and enforcement. Deterministic enforcement is substantive prior work and an important baseline |
| [PolicyShiftGuard / PolicyShiftBench](https://arxiv.org/abs/2607.05910) | Tests policy-dependent image decisions using matched policy conditions and held-out policies. Policy-conditioned counterfactual testing itself is already explored, although this work targets images |
| [Safety, or Just Capability?](https://arxiv.org/abs/2607.28685) | Recent validity audit of agent-safety benchmarks. Relevant to separating safety from weak task capability and detecting misleading aggregate scores; treat it as a preprint |
| [PINT](https://github.com/lakeraai/pint-benchmark) | Injection detection and benign lookalikes. Useful component test; the linked repository is archived, so verify maintained lineage |
| [JevBench](https://github.com/fstandhartinger/jevbench) | Useful decision-interface comparator; retain original suite/version and scoring. This review has not established a dedicated peer-reviewed benchmark paper |

## What remains open after this review

A plausible research question is: **How well do compact guards authorize proposed tool actions under unseen policies and incomplete evidence, at a fixed human-review budget?**

This is a candidate contribution, not verified novelty. Before claiming a first, expand the literature search on action authorization, policy-conditioned guards, selective prediction, conformal risk control, and human deferral. Compare dataset schemas and released evaluation code, not only abstracts. The existing studies above already cover significant parts of this problem.

The practical first result should be an honest baseline report, including where Laya fails due to context limits or missing information. If a simple rules engine solves the chosen cases, that is evidence to redesign the research question rather than train a larger model.
