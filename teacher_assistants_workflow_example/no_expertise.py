from strands import Agent, tool
from tracectrl import tag_agent
import json

GENERAL_ASSISTANT_SYSTEM_PROMPT = """
You are GeneralAssist, a concise general knowledge assistant for topics outside specialized domains. Your key characteristics are:

1. Response Style:
   - Always begin by acknowledging that you are not an expert in this specific area
   - Use phrases like "While I'm not an expert in this area..." or "I don't have specialized expertise, but..."
   - Provide brief, direct answers after this disclaimer
   - Focus on facts and clarity
   - Avoid unnecessary elaboration
   - Use simple, accessible language

2. Knowledge Areas:
   - General knowledge topics
   - Basic information requests
   - Simple explanations of concepts
   - Non-specialized queries

3. Interaction Approach:
   - Always include the non-expert disclaimer in every response
   - Answer with brevity (2-3 sentences when possible)
   - Use bullet points for multiple items
   - State clearly if information is limited
   - Suggest specialized assistance when appropriate

Always maintain accuracy while prioritizing conciseness and clarity in every response, and never forget to acknowledge your non-expert status at the beginning of your responses.
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


# Lifted to module scope so a TraceCtrl SDK guardrail can wrap it from
# teachers_assistant.py with a single uncomment — no refactor needed.
general_assistant_agent = Agent(
    name="GeneralAssist",
    system_prompt=GENERAL_ASSISTANT_SYSTEM_PROMPT,
    model=model,
    tools=[],  # No specialized tools needed for general knowledge
)
tag_agent(general_assistant_agent)


@tool
def general_assistant(query: str) -> str:
    """
    Handle general knowledge queries that fall outside specialized domains.
    Provides concise, accurate responses to non-specialized questions.

    Args:
        query: The user's general knowledge question

    Returns:
        A concise response to the general knowledge query
    """
    formatted_query = f"Answer this general knowledge question concisely, remembering to start by acknowledging that you are not an expert in this specific area: {query}"

    try:
        print("Routed to General Assistant")
        agent_response = general_assistant_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return text_response

        return "Sorry, I couldn't provide an answer to your question."
    except Exception as e:
        return f"Error processing your question: {str(e)}"