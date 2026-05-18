#!/usr/bin/env python3
"""
# 📁 Teacher's Assistant Strands Agent

A specialized Strands agent that is the orchestrator to utilize sub-agents and tools at its disposal to answer a user query.

## What This Example Shows

"""

import os
import tracectrl
from tracectrl import tag_agent
from tracectrl.instrumentation.strands import StrandsInstrumentor
from strands import Agent
from strands_tools import file_read, file_write, editor
from english_assistant import english_assistant
from language_assistant import language_assistant
from math_assistant import math_assistant
from no_expertise import general_assistant

tracectrl.configure(
    service_name=os.getenv("TRACECTRL_SERVICE_NAME", "teachers-assistant"),
    endpoint=os.getenv("TRACECTRL_ENDPOINT", "http://localhost:4317"),
)
StrandsInstrumentor().instrument()


# Define a focused system prompt for file operations
TEACHER_SYSTEM_PROMPT = """
You are TeachAssist, a sophisticated educational orchestrator designed to coordinate educational support across multiple subjects. Your role is to:

1. Analyze incoming student queries and determine the most appropriate specialized agent to handle them:
   - Math Agent: For mathematical calculations, problems, and concepts
   - English Agent: For writing, grammar, literature, and composition
   - Language Agent: For translation and language-related queries
   - Computer Science Agent: For programming, algorithms, data structures, and code execution
   - General Assistant: For all other topics outside these specialized domains

2. Key Responsibilities:
   - Accurately classify student queries by subject area
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed

3. Decision Protocol:
   - If query involves calculations/numbers → Math Agent
   - If query involves writing/literature/grammar → English Agent
   - If query involves translation → Language Agent
   - If query involves programming/coding/algorithms/computer science → Computer Science Agent
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

import os
from strands.models.gemini import GeminiModel


def _make_gemini_model() -> GeminiModel:
    """Pick AI Studio (API key) or Vertex AI (service account) based on env."""
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        return GeminiModel(
            client_args={
                "vertexai": True,
                "project": os.environ["GOOGLE_CLOUD_PROJECT"],
                "location": os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
            },
            model_id=os.getenv("GOOGLE_MODEL_ID", "gemini-3.1-flash-lite-preview"),
        )
    return GeminiModel(
        client_args={"api_key": os.environ["GOOGLE_API_KEY"]},
        model_id=os.getenv("GOOGLE_MODEL_ID", "gemini-3.1-flash-lite"),
    )


model = _make_gemini_model()

# Create a file-focused agent with selected tools
teacher_agent = Agent(
    name="TeachAssist",
    system_prompt=TEACHER_SYSTEM_PROMPT,
    model=model,
    callback_handler=None,
    tools=[math_assistant, language_assistant, english_assistant, general_assistant],
)
tag_agent(teacher_agent)


# ---------------------------------------------------------------------------
# Optional: wrap TeachAssist (and the GeneralAssist specialist) with TraceCtrl
# SDK guardrails. To enable, uncomment the four lines below. The judge uses
# the same Gemini model — GOOGLE_API_KEY is already in scope. See
# guardrails/README.md for the pattern + test prompts.
#
# from tracectrl.guardrails import wrap_agent_with_guardrails
# from guardrails import pii_in_query_guard, code_execution_safety_guard
# from no_expertise import general_assistant_agent
# wrap_agent_with_guardrails(teacher_agent, [pii_in_query_guard])
# wrap_agent_with_guardrails(general_assistant_agent, [code_execution_safety_guard])
# ---------------------------------------------------------------------------


# Example usage
if __name__ == "__main__":
    print("\n📁 Teacher's Assistant Strands Agent 📁\n")
    print("Ask a question in any subject area, and I'll route it to the appropriate specialist.")
    print("Type 'exit' to quit.")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break

            response = teacher_agent(
                user_input, 
            )
            
            # Extract and print only the relevant content from the specialized agent's response
            content = str(response)
            print(content)
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
