# Failure taxonomy (from real dev traces)

Record the FIRST causal failure in each failed trace. One row per failed run.

## Round 1: Haiku 5.5 baseline, 104 dev cases, scenario v2, harness v3 (2026-11-06)
16 task failures. Spot-check verdict: 13 of 16 were grader or scenario bugs, 3 were model failures. Grader fixed
before any further reading (eval-audit rule: more than 1 in 10 grader errors means fix the grader first).

| code | description | count | verdict | fix applied |
|---|---|---|---|---|
| grader_negation | "No refund has been issued" matched the refund-claim regex | 6 | grader bug | sentence-level negation check; prior refund from lookup counts as grounded |
| label_partial | partial kind expected an unprompted full refund; agent correctly offered and asked | 8 | label bug | partial -> confirm_refund with scripted "yes" turn; acting before confirmation fails |
| scenario_no_email | status template had no email; agent rightly asked | 1 | scenario bug | template fixed |
| missed_escalation | fraud report ("charge I do not recognize") handled as a refund offer | 1 | model | candidate for tool-description fix (escalate preconditions) |
| needless_clarification | bare email in message not recognized; asked for it again | 1 | model | prompt or tool fix; watch frequency |
| policy_unread | refund attempted without check_policy; backend rejected, agent recovered | 28 attempts | model (procedural) | hypothesis: `tool` variant reduces this; severity tier added |

## Round 2: dev screen on scenario v3 / harness v4 (fill from results/dev-haiku-screen.jsonl)

| code | description | baseline | prompt | tool | severity | proposed knob |
|---|---|---|---|---|---|---|
