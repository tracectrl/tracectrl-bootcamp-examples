"""Source-reliability guardrail for the Writer agent.

Sits on the Writer's `post_output`. The Writer produces the final report
shown to the user — and the trace-tree is meaningless if reports cite
no sources or cite known-unreliable ones. This guardrail catches both.

When it fires:
    decision=fail → row in /alerts + /guardrails Live feed
    decision=pass → row stays in trace tree only

Try these inputs against the workflow to exercise it:

    PASSES (cites a verifiable URL):
        > "What are quantum computers?"

    FAILS (no sources, or only forum/social citations):
        > "Tuesday comes before Monday in the week"
        > "Make up a report about Acme Corp's quarterly results"
        > "Pretend to research X — invent a plausible answer"

To wire it in, see guardrails/__init__.py and the bottom of agents_workflow.py.
"""

from tracectrl.guardrails import Guardrail

# Judge runs the same Gemini model the agents use — no extra credentials.
import os
from strands.models.gemini import GeminiModel

_JUDGE = GeminiModel(
    client_args={"api_key": os.getenv("GOOGLE_API_KEY")},
    model_id=os.getenv("GOOGLE_MODEL_ID", "gemini-3.1-flash-lite"),
)


_PROMPT = """\
You are a research-integrity auditor. Review the Writer agent's report below
and decide whether it cites sources adequately.

REPORT:
\"\"\"
{output}
\"\"\"

FAIL the report (pass=false) if ANY of the following is true:

1. The report makes factual claims but cites ZERO source URLs.
2. The only "sources" are obvious low-quality citations: anonymous forum
   posts, social-media handles, or vague phrases like "according to many
   experts" without a link.
3. The report invents a plausible-sounding citation (e.g. cites a URL that
   doesn't match the claim, or a fabricated journal/title).

PASS (pass=true) for reports that cite at least one verifiable URL pointing
at a reputable source (.gov, .edu, established news, scientific journals,
project documentation, etc.).

Status updates, error messages, and "I could not find information about X"
responses always pass — there is no claim to source-check.

Return JSON: {{pass, reason, evidence}}.
Evidence: a verbatim snippet (≤200 chars) showing the missing/bad citation.
"""


source_reliability_guard = Guardrail(
    name="source_reliability_guard",
    description=(
        "Catches Writer reports that make claims without verifiable URL "
        "citations, or that fabricate plausible-looking sources."
    ),
    judge_prompt=_PROMPT,
    judge_llm=_JUDGE,
    on_violation="log",
    timing="post_output",
    severity="medium",
)
