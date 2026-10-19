# Support agent evaluation lab
Synthetic sandbox only. No company data, real refunds, or production traffic.

Start free:
```
python3 -m unittest -v
python3 lab.py generate
python3 lab.py run --dry-run --limit 10 --out results/dry.jsonl
python3 lab.py compare results/dry.jsonl
```
No API call happens without --allow-api. Dry fixture scores are NOT model results.

Python 3.11+ recommended. For paid mode and optional Phoenix:
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip freeze > requirements.lock.txt
phoenix serve
```
Run Phoenix in a second activated terminal. It listens on localhost:6006. Do not expose the port publicly.
In the first activated terminal, set OPENAI_API_KEY privately via your OS/password manager. Never commit it or send it in chat.
Paid smoke test (explicitly spends API credits):
```
python lab.py run --allow-api --phoenix --split dev --limit 5 --variants baseline,prompt --budget 1 --out results/smoke.jsonl
python lab.py compare results/smoke.jsonl
```
The --budget flag conservatively reserves $0.05 per agent run / $0.02 per judge call. It is not a provider-enforced hard cap. Rates assumed: gpt-4.1-mini standard $0.40/M input, $1.60/M output, checked Oct 12 2026. Recheck before paid use.
No automatic retries. API exceptions stop the batch and preserve completed rows; billed tokens from a failed call may not appear in estimates. Judge exceptions also preserve previously completed scores.

The code checker handles actual actions, not every failure: false success claims require review/judge; verify/deny cases are only checked for no successful refund. Count unsafe attempts independently. A timeout or empty answer must not be hidden behind a passing action check.

Run prompt-only and tool-description-only variants on development cases. Choose ONE before opening the frozen test set. Regenerating data is deterministic, but do not edit test cases after observing results without declaring a new version.

Optional judge:
```
python lab.py label results/smoke.jsonl --limit 50
python lab.py judge results/smoke.jsonl --allow-api --budget 1 --out results/judges.jsonl
python lab.py validate --labels labels/review.csv --scores results/judges.jsonl
```
Fill human_fail with 1 for unsupported success claims and 0 otherwise before examining judge scores. These are pilot labels only. Use a disjoint judge-development and judge-test family split for final calibration; this starter does not automate that split. Keep the final agent-test set unseen until the judge and variant are frozen. Stratify by failure class and ensure positive/negative examples exist. Label synthetic counterexamples separately rather than silently mixing them into outcome estimates.

Limits: no user simulator/multi-turn identity flow, no retrieval, no production A/B, no validated subjective judge yet. Tracer records manual agent/model/tool spans; export includes prompts and fictional data. Pin dependencies after successful installation; package setup and real API execution were not run during scaffold creation.
