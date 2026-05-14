"""Guardrails for the teacher-assistants workflow example.

Each guardrail lives in its own file with its rubric prompt and example
test inputs. The recipe to wire them in:

    from tracectrl.guardrails import wrap_agent_with_guardrails
    from guardrails import pii_in_query_guard, code_execution_safety_guard

    wrap_agent_with_guardrails(teacher_agent, [pii_in_query_guard])
    wrap_agent_with_guardrails(general_assistant, [code_execution_safety_guard])

Each `wrap_agent_with_guardrails` call ALSO emits a registration span so
the guardrail shows up on /guardrails immediately, even before its first
evaluation.

See README.md in this directory for the full pattern + how to test.
"""

from guardrails.pii_in_query_guard import pii_in_query_guard
from guardrails.code_execution_safety_guard import code_execution_safety_guard

__all__ = ["pii_in_query_guard", "code_execution_safety_guard"]
