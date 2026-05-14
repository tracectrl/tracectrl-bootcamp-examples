#!/usr/bin/env python3
"""
# Agentic Workflow: Research Assistant

This example demonstrates an agentic workflow using Strands agents with web research capabilities.

## Key Features
- Specialized agent roles working in sequence
- Direct passing of information between workflow stages
- Web research using http_request and retrieve tools
- Fact-checking and information synthesis

## How to Run
1. Navigate to the example directory
2. Run: python agents_workflow.py
3. Enter queries or claims at the prompt

## Example Queries
- "Thomas Edison invented the light bulb"
- "Tuesday comes before Monday in the week"

## Workflow Process
1. Researcher Agent: Gathers web information using multiple tools
2. Analyst Agent: Verifies facts and synthesizes findings
3. Writer Agent: Creates final report
"""

import os
import tracectrl
from tracectrl import tag_agent
from tracectrl.instrumentation.strands import StrandsInstrumentor

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands_tools import http_request

tracectrl.configure(
    service_name=os.getenv("TRACECTRL_SERVICE_NAME", "agents-workflow"),
    endpoint=os.getenv("TRACECTRL_ENDPOINT", "http://localhost:4317"),
)
StrandsInstrumentor().instrument()

model = GeminiModel(
    client_args={
        "api_key": os.getenv("GOOGLE_API_KEY"),
    },
    model_id=os.getenv("GOOGLE_MODEL_ID", "gemini-3.1-flash-lite"),
)

@tool
def call_writer(analysis: str) -> str:
    """
    Hand off analysis to the Writer Agent to produce the final report.

    Args:
        analysis: The analysis produced by the Analyst Agent.

    Returns:
        The final report produced by the Writer Agent.
    """
    print("Step 3: Writer Agent creating final report...")

    writer_agent = Agent(
        name="Writer",
        model=model,
        system_prompt=(
            "You are a Writer Agent that creates clear reports. "
            "1. For fact-checks: State whether claims are true or false "
            "2. For research: Present key insights in a logical structure "
            "3. Keep reports under 500 words with brief source mentions"
        ),
        callback_handler=None,
    )
    tag_agent(writer_agent)

    result = writer_agent(
        f"Create a report based on this analysis:\n\n{analysis}"
    )

    print("Report creation complete")
    return str(result)


@tool
def call_analyst(research_findings: str) -> str:
    """
    Hand off research findings to the Analyst Agent for verification and synthesis.
    The Analyst will then call the Writer Agent to produce the final report.

    Args:
        research_findings: The raw research gathered by the Researcher Agent.

    Returns:
        The final report produced by the downstream writer stage.
    """
    print("Analysis complete")
    print("Passing analysis to Writer Agent...\n")
    print("Step 2: Analyst Agent analyzing findings...")

    analyst_agent = Agent(
        name="Analyst",
        model=model,
        system_prompt=(
            "You are an Analyst Agent that verifies information. "
            "1. For factual claims: Rate accuracy from 1-5 and correct if needed "
            "2. For research queries: Identify 3-5 key insights "
            "3. Evaluate source reliability and keep analysis under 400 words "
            "4. When your analysis is complete, call the call_writer tool with your analysis "
            "to produce the final report."
        ),
        callback_handler=None,
        tools=[call_writer],
    )
    tag_agent(analyst_agent)

    result = analyst_agent(
        f"Analyze these findings:\n\n{research_findings}\n\n"
        "When you have finished your analysis, call call_writer with your analysis."
    )

    return str(result)


def run_research_workflow(user_input):
    """
    Run a three-agent workflow for research and fact-checking with web sources.
    Shows progress logs during execution but presents only the final report to the user.

    Args:
        user_input: Research query or claim to verify

    Returns:
        str: The final report from the Writer Agent
    """

    print(f"\nProcessing: '{user_input}'")

    # Step 1: Researcher Agent — entry point for the chain.
    # It calls call_analyst as a tool, which in turn calls call_writer,
    # producing the nested AGENT spans that TraceCtrl needs for topology edges.
    print("\nStep 1: Researcher Agent gathering web information...")

    researcher_agent = Agent(
        name="Researcher",
        model=model,
        system_prompt=(
            "You are a Researcher Agent that gathers information from the web. "
            "1. Determine if the input is a research query or factual claim "
            "2. Use your research tools (http_request) to find relevant information "
            "3. Include source URLs and keep findings under 500 words "
            "4. When research is complete, call the call_analyst tool with your findings "
            "to pass them on for analysis."
        ),
        callback_handler=None,
        tools=[http_request, call_analyst],
    )
    tag_agent(researcher_agent)

    print("Research complete")
    print("Passing research findings to Analyst Agent...\n")

    final_report = researcher_agent(
        f"Research: '{user_input}'. Use your available tools to gather information from reliable sources. "
        f"Focus on being concise and thorough, but limit web requests to 1-2 sources. "
        f"When done, call call_analyst with your findings."
    )

    # Return the final report
    return final_report


# ---------------------------------------------------------------------------
# Optional: wrap the Analyst / Writer with TraceCtrl SDK guardrails.
# See guardrails/README.md for the pattern + test prompts. To enable:
#   1. Lift `analyst_agent` and `writer_agent` to module scope (currently
#      they're constructed inside the @tool functions above).
#   2. Uncomment the block below.
#   3. Make sure `aws configure` is set — the judge runs on Bedrock.
#
# from tracectrl.guardrails import wrap_agent_with_guardrails
# from guardrails import source_reliability_guard, fact_check_consistency_guard
#
# wrap_agent_with_guardrails(writer_agent,  [source_reliability_guard])
# wrap_agent_with_guardrails(analyst_agent, [fact_check_consistency_guard])
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Print welcome message
    print("\nAgentic Workflow: Research Assistant\n")
    print("This demo shows Strands agents in a workflow with web research.")
    print("Try research questions or fact-check claims.")
    print("\nExamples:")
    print("- \"What are quantum computers?\"")
    print("- \"Lemon cures cancer\"")
    print("- \"Tuesday comes before Monday in the week\"")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye!")
                break

            # Process the input through the workflow of agents
            final_report = run_research_workflow(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try a different request.")
