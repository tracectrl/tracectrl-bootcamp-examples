# Guardrails — Research Workflow

Scaffolding for wrapping the Researcher → Analyst → Writer chain with
TraceCtrl SDK guardrails. Each guardrail is a small dataclass: an LLM judge,
a rubric prompt, and a few config knobs.

## What's in this folder

| File | Sits on | What it flags |
|------|---------|---------------|
| `source_reliability_guard.py` | Writer, `post_output` | Reports that cite zero URLs or fabricated/low-quality sources |
| `fact_check_consistency_guard.py` | Analyst, `post_output` | Verdicts that contradict the evidence the Analyst itself cites |

The full rubric prompt + concrete test inputs live at the top of each file.

## The SDK pattern (~6 lines)

```python
from tracectrl.guardrails import Guardrail, wrap_agent_with_guardrails
from strands.models.gemini import GeminiModel
import os

judge = GeminiModel(
    client_args={"api_key": os.getenv("GOOGLE_API_KEY")},
    model_id=os.getenv("GOOGLE_MODEL_ID", "gemini-3.1-flash-lite"),
)

my_guard = Guardrail(
    name="my_guard",
    description="What this checks for, in one sentence.",
    judge_prompt="...",                # use {output} for post_output, {input} for pre_input
    judge_llm=judge,
    on_violation="log",                # only "log" works today; "block" is v2
    timing="post_output",              # or "pre_input"
    severity="medium",                 # low | medium | high | critical
)

wrap_agent_with_guardrails(my_agent, [my_guard])
```

Three knobs to decide on for each guardrail: **what** to check (the rubric
in `judge_prompt`), **when** to check (`timing`), and **how loud** to be
when it fails (`severity` + `on_violation`). The SDK handles span
attribution, evidence capture, and registration in `/guardrails`.

The judge uses the **same Gemini model your agents use** — same
`GOOGLE_API_KEY`, no extra credentials to provision.

## Wiring in (when you're ready)

Open `agents_workflow.py` and uncomment the wire-in block at the bottom.
The block looks like:

```python
# from tracectrl.guardrails import wrap_agent_with_guardrails
# from guardrails import source_reliability_guard, fact_check_consistency_guard
#
# wrap_agent_with_guardrails(writer_agent, [source_reliability_guard])
# wrap_agent_with_guardrails(analyst_agent, [fact_check_consistency_guard])
```

Note that `writer_agent` and `analyst_agent` are created *inside* the
`@tool` functions in the current example, so you'll need to lift them to
module scope (or wrap the references right after creation inside the tool)
before you can pass them to `wrap_agent_with_guardrails`. The simplest
move: refactor `writer_agent` / `analyst_agent` to module-level constants.

## How to test

Run the workflow with one of the failing prompts listed at the top of each
guardrail file:

```bash
./run_agents_workflow.sh
> Pretend to research X — invent a plausible answer
```

After ~10s (one OTel batch tick), open:

- **http://localhost:3000/guardrails** — your guardrail appears as a card
  with `monitoring` mode, `post_output` timing, and a count of recent
  evaluations.
- **http://localhost:3000/sessions** — click into the trace; you'll see a
  `tracectrl.guardrail.evaluation` span under Writer (or Analyst) with
  `decision=fail` and the verbatim evidence snippet.
- **http://localhost:3000/alerts** — fails stream into the live alerts feed
  in real time.
