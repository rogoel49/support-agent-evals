# Ship memo: hardened tool descriptions for the Acme support agent

**Decision:** _pending frozen test run_

**Audience and metric contract.** Support leadership wants correct resolution; finance wants no unauthorized
refunds; the customer wants a clear next step. Primary metric is `task_success` (right end state in the
environment plus a response that communicates the right disposition, with no unsupported claim). Guardrails are
severe unsafe refund attempts, unsupported success claims, and unnecessary escalations. Secondary are LLM calls,
latency, and dollars per successful case. Full contract: `docs/metric-contract.md`.

**Decision rule, fixed before the test run.** Advance the challenger if, on the frozen test split with 3 repeats:
(1) no severe unsafe attempt category increases; (2) unsupported claims do not increase; (3) `task_success` pass@1
is not worse than baseline by more than 2 points with the family-bootstrap interval, and either pass^3 or cost per
success improves materially. Hold if the interval on task_success straddles a 2-point regression. Reject if any
guardrail regresses.

**Frozen versions.**
- Scenario set v4, 300 cases, sha256 `0bedab704b93603e`, test split = families 7-9 (90 cases, 45 independent families)
- Harness v5 (`lab.py`), dependencies in `requirements.lock.txt` (anthropic 1.15.0, arize-phoenix 20.23.0)
- Agent model `claude-haiku-5-5`, effort low, max_tokens 1024, no server-side fallbacks, served model asserted per call
- Baseline: plain tool descriptions. Challenger `tool`: hardened tool descriptions stating each tool's preconditions (one field changed; see `VARIANTS` in `lab.py`)
- Judge: `claude-opus-5-5`, rubric `judge_prompt.txt`, four binary criteria via structured output

**Why this challenger.** Reading baseline traces, the dominant failure was procedural: the agent called `issue_refund`
before `check_policy`, the backend rejected it, and the agent recovered with an extra call. 41 of 120 dev runs did
this; Opus 5.5 did it too (5 of 30), so it is not a small-model quirk. The agent did not know a precondition of the
tool, so the fix belongs in the tool description. The hardened descriptions eliminated all 41 attempts on dev and
cut calls per run from 4.1 to 3.4. The prompt variant achieved the same on dev; tool was cheaper and the mechanism
is more specific, so it was frozen as the single challenger.

**Dev evidence (not the claim).** 120 dev cases, Haiku 5.5, one rep. task_success baseline 0.975 vs tool 0.992;
procedural unsafe attempts 41 vs 0; severe 0 vs 0; cost per run $0.00078 vs $0.00063; p50 model latency 5.3 s vs 4.4 s.
The effort variant (medium) matched tool on outcomes but kept 43 procedural attempts: more thinking does not supply a
missing precondition. One failure mode survives every variant: "a charge I do not recognize" is treated as a refund
request rather than suspected fraud (see below).

**Frozen test result.** _pending_

**Safety.** _pending_

**Judge calibration.** Judge: Claude Opus 5.5 at low effort, four binary criteria, structured output. Validation set:
60 rows from the judge split (baseline and tool arms mixed, variant hidden), of which 50 are real outputs and 10 are
fabricated success claims inserted as counterexamples. Labels came from a second model (Claude Fable 5.1), not a
human; they must be redone by a human before this judge steers a decision. On the `grounded` criterion:

| set | n | TP | FP | FN | TN | precision | recall | agreement | majority-class agreement |
|---|---|---|---|---|---|---|---|---|---|
| counterexamples (sensitivity) | 10 | 10 | 0 | 0 | 0 | 1.00 | 1.00 | 1.00 | n/a |
| real rows | 50 | 0 | 2 | 0 | 48 | n/a (no true positives) | n/a | 0.96 | 1.00 |

No real output in the judge split contained an unsupported refund, escalation, lookup, or verification claim, so
precision and recall on real traffic are undefined and the counterexample recall is the only sensitivity evidence.
Both disagreements on real rows are the same case: the agent said it "passed your feedback along to the team" with
no tool behind it. The reviewer labeled it 0 (outside the rubric's four action types, noted as borderline at label
time); the judge called it ungrounded. That is a rubric-boundary decision for the human labeler, not a judge
defect, and it is arguably the judge being right. Other criteria on real rows: disposition 0.98, next_step 1.00,
no_promises 0.96; the misses are defensible strict readings (e.g. "I'll help you with the refund" before
eligibility is known). Judge cost: $0.70 for 60 rows, tracked separately from agent cost. Status: advisory. The ship
decision below rests on code checks and read traces, not on judge scores.

**Cost and latency.** _pending_

**One failed trace, root cause, fix.** _pending_

**Limitations.** Synthetic, fictional data; one scripted follow-up turn; no retrieval; regex-based disposition checks
that were corrected twice after reading real traces; 45 independent test families, so intervals are wide; judge and
agent are the same model family; labels for judge calibration came from a second model (Claude Fable 5.1), not a
human, and must be replaced by human labels before the judge is used to steer decisions.

**Proposed online test (not executed).** Randomize at the customer-account level with persistent assignment, since
users within an account share policy state. Primary metric: correct resolution as judged by a human-audited sample
plus end-state checks from the backend (refund issued when and only when policy allows). Guardrails: unauthorized
refund attempts per 1,000 conversations, false success claims, escalation rate split into required vs unnecessary.
Secondary: cost and latency per conversation. Power: from the dev-split variance, detecting a 3-point change in
resolution at 80 percent power needs on the order of a few thousand conversations per arm; compute from the pilot
before launch. Stop and roll back if any guardrail crosses its baseline upper bound in a daily check. Variance
reduction with a pre-period covariate (CUPED) only if a per-account pre-treatment resolution rate exists; otherwise
stratify by intent. No production deployment is authorized by this memo.
