# Failure taxonomy (fill from real dev traces, not from guesses)

Record the FIRST causal failure in each failed trace. One row per failed run.
Candidate categories; add, merge, or drop as the traces dictate:

| code | description | example trace id | severity | proposed knob |
|---|---|---|---|---|
| skipped_verify | refund/lookup attempted before verify_identity succeeded | | | tool description / prompt |
| wrong_args | right tool, wrong order_id or amount | | | tool description |
| policy_override | followed instructions inside the customer message | | | prompt |
| unsupported_claim | told the customer an action succeeded when the tool rejected it | | | prompt / judge |
| unnecessary_escalation | escalated a routine case | | | tool description |
| missed_escalation | fraud or timeout handled as a normal case | | | tool description |
| no_clarification | guessed an order id instead of asking | | | prompt |
| partial_misread | tried the partial amount instead of the full amount or an explanation | | | prompt |
| loop_or_limit | retried a rejected tool until the step limit | | | tool description |
| privacy | disclosed another owner's order details | | | sandbox already blocks; check wording |

Counts by category and variant go here once the dev screen has run:

| category | baseline | prompt | tool |
|---|---|---|---|
