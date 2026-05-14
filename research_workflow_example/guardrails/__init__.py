"""Guardrails for the research workflow example.

Each guardrail lives in its own file with its rubric prompt and example
test inputs. The recipe to wire them in:

    from tracectrl.guardrails import wrap_agent_with_guardrails
    from guardrails import source_reliability_guard, fact_check_consistency_guard

    wrap_agent_with_guardrails(writer_agent, [source_reliability_guard])
    wrap_agent_with_guardrails(analyst_agent, [fact_check_consistency_guard])

Each `wrap_agent_with_guardrails` call ALSO emits a registration span so
the guardrail shows up on /guardrails immediately, even before its first
evaluation.

See README.md in this directory for the full pattern + how to test.
"""

from guardrails.source_reliability_guard import source_reliability_guard
from guardrails.fact_check_consistency_guard import fact_check_consistency_guard

__all__ = ["source_reliability_guard", "fact_check_consistency_guard"]
