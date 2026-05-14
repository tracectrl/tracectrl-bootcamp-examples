# Guardrails — Teacher Assistants Workflow

Scaffolding for wrapping the TeachAssist orchestrator and its specialist
sub-agents with TraceCtrl SDK guardrails. Each guardrail is a small
dataclass: an LLM judge, a rubric prompt, and a few config knobs.

## What's in this folder

| File | Sits on | What it flags |
|------|---------|---------------|
| `pii_in_query_guard.py` | TeachAssist, `pre_input` | Student queries containing email, phone, national ID, or full-name + home-address pairing |
| `code_execution_safety_guard.py` | GeneralAssist, `post_output` | Code responses that emit shell-exec, destructive filesystem, or remote-payload patterns |

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
    judge_prompt="...",                # use {input} for pre_input, {output} for post_output
    judge_llm=judge,
    on_violation="log",                # only "log" works today; "block" is v2
    timing="pre_input",                # or "post_output"
    severity="medium",                 # low | medium | high | critical
)

wrap_agent_with_guardrails(teacher_agent, [my_guard])
```

Three knobs to decide on for each guardrail: **what** to check (the rubric
in `judge_prompt`), **when** to check (`timing`), and **how loud** to be
when it fails (`severity` + `on_violation`). The SDK handles span
attribution, evidence capture, and registration in `/guardrails`.

The judge uses the **same Gemini model your agents use** — same
`GOOGLE_API_KEY`, no extra credentials to provision.

## Wiring in (when you're ready)

Open `teachers_assistant.py` and uncomment the wire-in block at the bottom.
The block looks like:

```python
# from tracectrl.guardrails import wrap_agent_with_guardrails
# from guardrails import pii_in_query_guard, code_execution_safety_guard
# from no_expertise import general_assistant_agent
#
# wrap_agent_with_guardrails(teacher_agent,           [pii_in_query_guard])
# wrap_agent_with_guardrails(general_assistant_agent, [code_execution_safety_guard])
```

The specialist sub-agents (`math_assistant`, `general_assistant`, etc.) are
exposed as `@tool` functions in the other files. To wrap the underlying
agent objects you'll need to expose them at module scope (rename the inner
agent variable and import it) — currently the agents are constructed
inside the tool function bodies. The simplest move: lift each agent
construction out of its tool function so the agent is module-level and
the tool function just calls it.

## How to test

Run the workflow with one of the failing prompts listed at the top of each
guardrail file:

```bash
./run_agents_workflow.sh
> My name is Sarah Lee, ic S1234567A. Help me with my math hw: solve x^2 - 5x + 6 = 0
```

After ~10s (one OTel batch tick), open:

- **http://localhost:3000/guardrails** — your guardrails appear with
  `pre_input` / `post_output` timing and a count of recent evaluations.
- **http://localhost:3000/sessions** — click into the trace; you'll see a
  `tracectrl.guardrail.evaluation` span on the relevant agent turn with
  `decision=fail` and the verbatim evidence snippet.
- **http://localhost:3000/alerts** — fails stream into the live alerts feed
  in real time.
