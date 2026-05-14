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
from strands.models import BedrockModel

judge = BedrockModel(model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    region_name="us-east-1")

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

## ⚠️ The judge runs on AWS Bedrock

The TraceCtrl SDK invokes the judge via Bedrock's `converse` API.
This bootcamp's agents run on Gemini (Google AI Studio is free); the
**judge is a separate Bedrock call**. To run guardrails for real you
need:

```bash
aws configure       # AWS access key + secret, region us-east-1
# AND enable model access for the chosen Claude model in the AWS Bedrock console
```

No Bedrock access? Two options:

1. **Read-only mode** — open the files, understand the pattern, skip the
   wire-in step. You'll still see how `Guardrail` is defined and how the
   rubric is structured.
2. **Custom judge** — replace `BedrockModel` with a thin class that calls
   your preferred LLM and exposes `.model_id` + `.region_name` attributes.
   The SDK's internal `invoke_judge` hard-codes boto3, so this requires
   a small SDK fork. Out of scope for the bootcamp.

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
