"""PII-in-query guardrail for the TeachAssist orchestrator.

Sits on TeachAssist's `pre_input`. Educational tools commonly have students
paste in their own homework — which sometimes carries PII riders like email
addresses, phone numbers, or "my name is X and I live at Y" framing. This
guardrail flags those queries so a school admin can see them on the
Guardrails dashboard.

Try these inputs against the workflow to exercise it:

    PASSES (normal student questions):
        > "Solve x^2 - 5x + 6 = 0"
        > "What is the difference between affect and effect?"
        > "Translate 'good morning' to Japanese"

    FAILS (PII in the query):
        > "My name is Sarah Lee, ic S1234567A. Help me with my math hw:
           solve x^2 - 5x + 6 = 0"
        > "Email me the answer at student@school.edu — what's the past
           tense of swim?"
        > "I live at 12 Bukit Timah Road and my phone is +65 9123 4567.
           Translate hello to French."

To wire it in, see guardrails/__init__.py and the bottom of teachers_assistant.py.
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
You are a privacy auditor for a school-facing AI tutor. Review the student
query below and decide whether it contains PII (personally identifiable
information) that should not be sent to a public LLM.

QUERY:
\"\"\"
{input}
\"\"\"

FAIL the query (pass=false) if it contains ANY of:

1. Email address — anything matching name@domain.tld.
2. Phone number — recognisable sequences of digits in phone format.
3. National ID / SSN — e.g. Singapore NRIC (S1234567A), US SSN
   (XXX-XX-XXXX), UK NI number.
4. Full name + location pairing — "My name is X, I live at Y/at school Z".
5. Date of birth combined with a name.

DO NOT FAIL on:
- The student's first name alone ("Hi I'm Sarah, help with...").
- Generic education context ("for my class", "for my homework").
- Names of historical/public figures inside the question itself.

Return JSON: {{pass, reason, evidence}}.
Evidence: the verbatim PII substring (≤200 chars) — the school will use
this to message the student about safer query habits.
"""


pii_in_query_guard = Guardrail(
    name="pii_in_query_guard",
    description=(
        "Flags student queries that contain PII (email, phone, national ID, "
        "home address paired with a name). Logs only — does not block."
    ),
    judge_prompt=_PROMPT,
    judge_llm=_JUDGE,
    on_violation="log",
    timing="pre_input",
    severity="medium",
)
