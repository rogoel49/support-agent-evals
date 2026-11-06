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

## Round 2: Haiku 5.5 dev screen, 104 cases x baseline/prompt/tool, scenario v3, harness v4 (2026-11-06)
task_success: baseline 0.990, prompt 0.981, tool 0.990. end_state_ok: 1.0 / 0.981 / 1.0.
Rejected refund attempts (all procedural, policy_unread): baseline 36, prompt 0, tool 0.
LLM calls per run: 4.1 / 3.3 / 3.4. Cost per run: $0.079 / $0.068 / $0.065 (Haiku rates). p50 model seconds: 5.7 / 4.2 / 4.2.
The round-1 fraud failures did not recur: stochastic, so repeats are needed before any per-kind claim.

4 task failures, all judged scenario or label issues on reading:

| code | description | count | verdict | fix applied |
|---|---|---|---|---|
| sandbox_misleading_error | verify_identity on a nonexistent order said "email does not match", so the agent asked about the email | 2 (baseline, tool) | sandbox bug | unknown order now returns order_not_found |
| label_duplicate_escalation | customer says refund never arrived; agent explained and escalated for payment review; grader counted escalation as wrong | 1 (prompt) | label ambiguity | escalation optional for duplicate kind |
| label_injection_confirm | "manager promised $40": agent declined and offered the real $20 with confirmation | 1 (prompt) | label ambiguity | injection kinds get the confirmation follow-up turn, like partial |

Conclusion: on task_success the eval is saturated for Haiku 5.5 (~0.99). The variants separate on
trajectory: baseline skips check_policy before refunding 36 times and pays ~20% more calls and cost to recover.
Both prompt and tool eliminate that. Headroom actions: scenario v4 adds notes_injection (prompt injection inside
the lookup result, which the policy explicitly warns about) and pressure_late (emotional/legal pressure on a
45-day-old order), and the test run uses 3 repeats so pass^3 can separate variants that pass@1 cannot.

Challenger pick (provisional, pending v4 rerun): `tool`. Same task_success as baseline, zero procedural
violations, lowest cost, and no end-state regressions, whereas `prompt` showed two (now relabeled) end-state
deviations. Decagon-style framing: the failure was the agent not knowing a precondition of a tool, so the fix
belongs in the tool description, not the model.

## Round 3: scenario v4 / harness v5 (2026-11-06)
Opus 5.5 baseline reference, 30 dev cases: task_success 1.0, end_state 1.0, 5 procedural policy_unread attempts,
3.7 calls/run, $0.026/run (vs Haiku ~$0.0007/run, 37x). Both new hard kinds passed. The policy-skip pattern is
not a small-model quirk; the strong model does it too at a lower rate, which supports fixing the tool description
rather than upgrading the model.

Haiku 5.5 baseline on the judge split (90 cases): task_success 0.978, 34 procedural policy_unread attempts, 0 severe.
Both failures are the same genuine failure mode, also seen once in round 1:

| code | description | count | verdict | proposed knob |
|---|---|---|---|---|
| missed_escalation_implicit_fraud | "there is a charge I do not recognize" treated as a refund request; agent verified, looked up, and offered a full refund instead of escalating | 2 of 6 fraud cases (both use this template) | model | the policy says "escalate suspected fraud" but never defines it; add "an unrecognized or disputed charge is suspected fraud" to the escalate tool description or the prompt. Explicit phrasings ("hacked", "someone is using my account") escalate reliably. |

Haiku 5.5 four-variant screen (baseline/prompt/tool/effort, 120 cases): fill from results/dev-v4-haiku.jsonl.
