# support-agent-evals

Synthetic support-agent evaluation lab. Portfolio project for agent data science
(trace-based error analysis, LLM-judge calibration, paired offline evals, ship memo).
Everything here is fictional: no real customer data, credentials, or production traffic.

## Rules
- `lab.py run` never calls an API unless `--allow-api` is passed. Keep it that way.
- Project spend ceiling is $10 total, with a stop-and-review at $2. Check `estimated_usd` in results.
- Never commit `.env`, API keys, `data/`, `results/`, or `labels/` (already gitignored).
- Test split (`split == test`) is frozen: do not look at or tune on it until one challenger is chosen on dev.
- Change one knob per variant: `prompt` (system prompt only) vs `tool` (tool descriptions only).
- Dry-fixture scores are plumbing checks, never model performance.

## Commands
```
.venv/bin/python -m unittest -v
.venv/bin/python lab.py generate
.venv/bin/python lab.py run --dry-run --limit 10 --out results/dry.jsonl
.venv/bin/python lab.py compare results/dry.jsonl
phoenix serve          # second terminal, http://localhost:6006
```
Model: gpt-4.1-mini via OpenAI. Tracing: local Arize Phoenix (OpenInference spans).
See README.md for the full workflow and docs/ for the metric contract and ship memo templates.
