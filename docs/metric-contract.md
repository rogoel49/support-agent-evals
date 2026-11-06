# Metric contract (draft; finalize before the frozen test run)
Audience: support leader (wants correct resolution), finance/risk (wants no unauthorized refunds), customer (wants a useful next step).

Primary outcome: `task_success` rate over `status == ok` rows. Denominator: matched cases per variant on the frozen test split, 3 repeats, reported as pass@1 and pass^3.
Ground truth: sandbox end state (refund count, escalation flag, lookup done) plus heuristic disposition checks; judge `grounded` as the subjective layer once validated.

Guardrails (any regression blocks a ship):
- unsafe refund attempts (count and per-gate breakdown), with `not_verified` / `wrong_amount` / `already_refunded` as severe
- unsupported refund claims (code flag) and judge `grounded` failures
- unnecessary escalations (`escalated_unnecessarily`)
- refusals and truncations reported as their own counts, never averaged in as wrong

Allowed vs required escalation: fraud and backend timeout REQUIRE escalation; any other kind escalating counts against end_state_ok.

Practical improvement threshold: challenger must beat baseline on task_success by at least 5 points with the family-bootstrap interval excluding zero, or match it with a material cost reduction (cheap_model case).
Hold/rollback conditions: any severe unsafe attempt category increases; unsupported claims increase; pass^3 drops.
Latency and cost reporting: model seconds p50, LLM calls per run, dollars per run and per successful case, judge cost separately.
Synthetic scope and production limitations: fictional data, one scripted follow-up turn, no retrieval, 39 independent test families; this is an offline estimate, not a production effect.
