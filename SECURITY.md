# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub: open the **Security**
tab of this repository and choose **Report a vulnerability**. Do not open a
public issue for a security problem.

Include what you found, the file or command involved, and the steps to
reproduce it. We aim to acknowledge reports within five working days.

## Scope

JevBench is an evaluation harness. The areas where a security problem matters
most are:

- **API keys.** `run_eval.py` reads the hosted model's key from the
  `TYPESAFE_API_KEY` environment variable. It must never be written to
  predictions, logs or error messages. Any path that leaks it is in scope.
- **Released artifacts.** Predictions must never contain source text, and
  sources whose licence forbids redistribution (SST-5) must be released without
  their text. `workspace/stage_release.py` checks both before a release.
- **Leakage into requests.** Adapters send only allowlisted dataset fields. A
  path by which a gold label or rationale reaches a model request is a
  correctness bug and should be reported the same way.

## Adversarial content in the datasets

Several slices (prompt injections, jailbreak attempts, unsafe prompts, agent
trajectories) contain adversarial text by design. The harness treats this text
as data: it is never executed, and every safety question tells the model to
treat the state as untrusted. A dataset row that manages to change the
harness's own behaviour is in scope.

## Supported versions

Only the latest release is supported.
