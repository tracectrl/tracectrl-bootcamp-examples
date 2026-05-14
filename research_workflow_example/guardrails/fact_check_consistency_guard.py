"""Fact-check consistency guardrail for the Analyst agent.

Sits on the Analyst's `post_output`. The Analyst takes raw findings from the
Researcher and produces a verdict (true / false / accuracy rating). A common
failure mode in agentic workflows is the Analyst's *verdict* not matching the
*evidence it cites* — for example, finding that a claim is false but writing
"this claim is accurate" because the LLM picked up the wrong vibe from the
prompt. This guardrail catches that internal inconsistency.

Try these inputs against the workflow to exercise it:

    PASSES (verdict matches evidence):
        > "Thomas Edison invented the light bulb"
            → Analyst says "partially false, Edison improved an existing
              design" with sources backing that. Internally consistent. PASS.

    FAILS (verdict contradicts evidence):
        > "Lemons cure cancer"
            → if the Analyst says "this is true" while the evidence it cites
              says no clinical trials support it, the verdict contradicts
              the evidence. FAIL.

    PASSES (clean factual):
        > "What is the chemical formula for water?"

To wire it in, see guardrails/__init__.py and the bottom of agents_workflow.py.
"""

from tracectrl.guardrails import Guardrail

# Judge uses Bedrock — see source_reliability_guard.py for the rationale.
from strands.models import BedrockModel

import os

_JUDGE = BedrockModel(
    model_id=os.getenv(
        "TRACECTRL_GUARDRAIL_JUDGE_MODEL",
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    ),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)


_PROMPT = """\
You are a fact-checking quality auditor. Review the Analyst agent's output
below and decide whether its overall verdict is INTERNALLY CONSISTENT with
the evidence it cites.

ANALYST OUTPUT:
\"\"\"
{output}
\"\"\"

FAIL the output (pass=false) ONLY when:

1. The Analyst gives an accuracy rating (e.g. "4/5", "mostly true",
   "false") AND the supporting points it lists clearly contradict that
   rating. Example: rating="true" while the cited evidence shows "no
   peer-reviewed study supports this".

2. The Analyst says "verified" / "confirmed" / "accurate" but provides no
   supporting points at all — verdict-without-evidence is also a fail.

PASS for outputs that are simply *uncertain* ("evidence is mixed", "cannot
determine") — uncertainty is a valid stance, not a contradiction.
PASS for research summaries that don't make a true/false claim at all.

Return JSON: {{pass, reason, evidence}}.
Evidence: the verdict phrase + the contradicting evidence snippet (≤200 chars).
"""


fact_check_consistency_guard = Guardrail(
    name="fact_check_consistency_guard",
    description=(
        "Catches Analyst outputs where the verdict (true/false/rating) "
        "contradicts the evidence the Analyst itself cites."
    ),
    judge_prompt=_PROMPT,
    judge_llm=_JUDGE,
    on_violation="log",
    timing="post_output",
    severity="high",
)
