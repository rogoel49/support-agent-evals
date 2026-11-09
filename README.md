# Support agent evaluation lab

How do you know an AI customer-support agent is safe to ship? This project builds a small fake support agent, then builds the measurement system around it: tests, a grader, a second AI that scores answers, a controlled comparison of two versions, and a one-page decision memo.

Everything is synthetic. No real customers, orders, money, or company data.

## The problem

Companies are replacing support chat with AI agents that can look up orders and issue refunds. The hard part is not building the agent. It is proving it does the right thing on the thousands of messy cases real customers send: wrong order numbers, expired refund windows, people claiming someone else's order, people trying to trick it with fake "manager approval".

## What I built

**A fake support agent.** It handles refund requests with five tools: verify who the customer is, look up the order, check the refund policy, issue a refund, or escalate to a human. A fake backend enforces the rules no matter what the agent asks for, so a bad decision is caught and logged instead of moving money.

**300 test conversations across 15 situations.** Simple status checks, valid refunds, refunds that are too late, customers who skip identity verification, customers who try to claim someone else's order, duplicate refund requests, fraud reports, and several attempts to manipulate the agent. Each situation has a known correct outcome.

**A grader that checks what happened, not what the agent said.** Did exactly one refund go through? Did it escalate when it should have? Did it ask for the customer's email before touching the account? Did it claim a refund was issued when none was?

**An AI judge for answer quality.** A stronger model reads each conversation and scores it on four yes/no questions. The judge was checked against reviewer labels and against deliberately fabricated answers to prove it catches lies.

**A controlled comparison.** Two versions of the agent, identical except for one change, run on the same held-out conversations three times each. The decision rule was written down before the test ran.

## What happened

Most of the early failures were my fault, not the model's. Three rounds of reading failed transcripts found more bugs in the grader and the test scenarios than in the agent. The grader flagged "no refund has been issued" as a false refund claim. One scenario expected the agent to refund the full amount when the customer asked for a partial one. The test suite was only trusted after a known-perfect agent scored 100% and a known-broken agent scored 0%.

Once the eval was trustworthy, the model's real failures were clear. The cheap model skipped the policy check before refunding about a third of the time. It also failed to treat "a charge I do not recognize" as fraud.

The change I tested: rewrite the five tool descriptions so each one states its preconditions. For example, the refund tool says it requires verification, a lookup, and a policy check first. The system prompt stayed the same.

## The result

On 90 held-out conversations, 3 repeats each, 540 runs with zero infrastructure errors:

| | before | after |
|---|---|---|
| correct outcome and correct answer | 98.1% | 98.5% |
| correct on all 3 repeats | 96.7% | 97.8% |
| refund attempts that would have moved money wrongly | 0 | 0 |
| refund attempts that skipped a required step | 95 of 270 | 0 of 270 |
| claimed a refund that did not happen | 0 | 0 |
| cost per conversation | $0.00076 | $0.00063 |

**Decision: ship the change.** Accuracy was already near the ceiling, so the gain is in reliability and cost, not correctness. The memo says exactly that. The "unrecognized charge" fraud miss survived both versions and is the next experiment.

The judge caught 10 of 10 fabricated success claims and agreed with the reviewer on 48 of 50 real answers. The two disagreements come down to one rubric question: does "I've passed your feedback to the team" count as an unbacked claim when no tool was called?

Total API spend for the whole project: about $3.90.

## Where to look

- `docs/ship-memo.md`: the decision, the pre-registered rule, the numbers, one root-caused failure, limitations, and a proposed online A/B test.
- `docs/failure-taxonomy.md`: four rounds of transcript reading, including the grader bugs.
- `docs/metric-contract.md`: what each metric means and what it does not.
- `artifacts/`: every run file behind the numbers above, judge scores, and the label sheet.
- `lab.py`: the whole harness in one file. `test_lab.py`: 21 unit tests.

## Technical notes

**Models.** Agent under test: Claude Haiku 5.5. Judge and reference run: Claude Opus 5.5. Anthropic Messages API with strict tool schemas. Server-side model fallbacks are off so the served model is always the one under test. Each run records the served model, token usage, and cost.

**Scenarios.** 15 kinds x 10 families x 2 paraphrases, generated deterministically from a seed. Families 0-3 are dev, 4-6 are for judge calibration, 7-9 are the frozen test set. Paraphrases in a family share order state and never cross splits. Every result row records the scenario file hash.

**Variants.** Each variant overrides exactly one field of the baseline config: system prompt addendum, hardened tool descriptions, cheaper model, or higher effort. One challenger is chosen on dev before the test split is touched.

**Metrics.** Primary: end state matches expected (refund count, escalation, lookup) plus the answer carries the right disposition and no unsupported claims. Guardrails: blocked refund attempts, split into severe gates (would have moved money wrongly) and procedural gates (skipped a step). Trajectory: calls, tokens, latency, as diagnostics only. Infrastructure failures (truncation, refusal, step limit, model mismatch) get their own status and never count as passes or fails.

**Statistics.** Paired by case, averaged per family, bootstrapped over families with 5000 resamples. Repeats give pass@1 and pass^k.

**Judge.** Four binary criteria via structured output: grounded, disposition, next step, no promises. Validated with precision, recall, agreement, and the majority-class baseline. Judge and agent share a model family, so the reviewer labels are what make it trustworthy. Current labels are from a disclosed second model; a human relabel is the open item.

**Tracing.** Local Arize Phoenix with OpenInference spans.

## Run it

```
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m unittest -v
python lab.py generate
python lab.py run --fixture oracle --split dev --limit 200 --variants baseline --quiet --out results/oracle.jsonl
python lab.py run --fixture null   --split dev --limit 200 --variants baseline --quiet --out results/null.jsonl
python lab.py compare results/oracle.jsonl   # ~1.0 everywhere
python lab.py compare results/null.jsonl     # task_success 0
```

No API call happens without `--allow-api`. For paid runs, put `ANTHROPIC_API_KEY` in a gitignored `.env`, then:

```
python lab.py run --allow-api --split dev --limit 5 --variants baseline,tool --model claude-haiku-5-5 --budget 1 --out results/smoke.jsonl
python lab.py compare results/smoke.jsonl
python lab.py show results/smoke.jsonl --failed
```

## Limits

One scripted follow-up turn, no retrieval, no production traffic. Answer checks are regexes and will miss phrasings on a new model, so read traces first. The test set has 45 independent families, so confidence intervals are wide. The judge labels still need a human pass.
