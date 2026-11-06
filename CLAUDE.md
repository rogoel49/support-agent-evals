# support-agent-evals

Synthetic support-agent evaluation lab. Portfolio project for agent data science
(trace-based error analysis, LLM-judge calibration, paired offline evals, ship memo).
Everything here is fictional: no real customer data, credentials, or production traffic.

## Rules
- `lab.py run` never calls an API unless `--allow-api` is passed. Keep it that way.
- Project spend ceiling is $10 total, with a stop-and-review at $2. Check `estimated_usd` in results.
- Never commit `.env`, API keys, `data/`, `results/`, or `labels/` (already gitignored).
- Test split (`split == test`) is frozen: do not look at or tune on it until one challenger is chosen on dev.
- Variants are configs in `VARIANTS` that each override exactly ONE field of `BASE` (prompt, tool, cheap_model, effort). Keep it that way.
- Run `--fixture oracle` and `--fixture null` after any grader change: oracle must be ~1.0, null task_success must be 0.
- Dry-fixture scores are plumbing checks, never model performance.

## Commands
```
.venv/bin/python -m unittest -v
.venv/bin/python lab.py generate
.venv/bin/python lab.py run --fixture oracle --limit 200 --variants baseline --quiet --out results/oracle.jsonl
.venv/bin/python lab.py run --fixture null --limit 200 --variants baseline --quiet --out results/null.jsonl
.venv/bin/python lab.py compare results/oracle.jsonl
phoenix serve          # second terminal, http://localhost:6006
```
Models: Claude via Anthropic Messages API (baseline claude-opus-5-5 at effort low; cheap_model variant claude-haiku-5-5; judge claude-opus-5-5). Key lives in .env (gitignored). Tracing: local Arize Phoenix (OpenInference spans).
Scenario set is v2 (260 cases, 13 kinds, five tools incl. verify_identity, scripted follow-up turn). Harness is v3: end-state grading, status field for infra failures, errors sidecar, repeats/pass^k, per-model cost.
`lab.py show <results> --failed` prints failed trajectories for error analysis.
See README.md for the full workflow and docs/ for the metric contract and ship memo templates.
