# Implementation report — v0.4.0

## Implemented

- external, read-only prompt directory via `--prompts-dir`;
- removal of operational `prompt_still_to_be_generated` / `prompts_used` concepts;
- paired sequential generation for every prompt: `with_skill`, then `without_skill`;
- filesystem isolation: Creation Skill is materialized only in the `with_skill` workspace;
- Creation Skill stored at `resources/skills/creation/SKILL.md`;
- Checker Skill stored at `resources/skills/checker/SKILL.md` and converted to automatic/non-interactive candidate-independent mode;
- checker schema stored at `resources/checker/config-schema.md` with checker 0.1.14 compatibility notes;
- one canonical `correction.yaml` generated only from prompt + Checker Skill + schema;
- exact same canonical correction passed to both checker executions;
- static LabValidator retained, including conservative prompt-required artifact checks, with framework resources (`Skill.md`, schema/correction) ignored and network/version false positives filtered;
- checker runs on copies under `checker-run/labs/candidate`, never directly on `source/`;
- deterministic pair comparator: WITH_SKILL_BETTER / WITHOUT_SKILL_BETTER / EQUAL / INCOMPARABLE;
- aggregate reports: CSV + JSON, with quality, technical reliability, and timing metrics kept separate;
- provider runners for Codex, Gemini CLI and Claude Code CLI;
- Claude runner uses `--safe-mode`, restricted `Read,Write,Edit` tools and no session persistence;
- dry-run compact by default and technical details behind `--verbose`;
- preflight for provider CLI, checker module, Kathara/backend, and non-consuming Gemini authentication behavior;
- manifests include experiment identity, variant, Skill enablement/hash, provider/model/reasoning, canonical correction hash, checker state and metrics;
- safe output-root marker and constrained per-experiment deletion;
- idempotent reuse of completed unchanged paired experiments;
- `status`, `compare`, and `validate` commands.

## Verification in this build environment

```text
PYTHONPATH=src python3 -m pytest -q
...............                                                          [100%]
15 passed
```

`python3 -m compileall -q src main.py` also completed successfully.

The editable package installation was verified with `pip install -e . --no-deps --no-build-isolation` and the console command displayed its CLI help successfully.

## Not executable inside the build container

A real end-to-end LLM/Kathara run was not executed here because this container does not have the user's authenticated Codex/Gemini/Claude environment, Kathara backend, or `kathara-lab-checker` installation. The included tests use deterministic fakes and verify orchestration, isolation, shared correction bytes, validators, runner command construction, comparison, and aggregation without consuming LLM quota.

Run `python3 main.py preflight --prompts-dir <dir>` on the target Mac before the first real experiment.
