# Strands Agents Example: Research Assistant Workflow

This example demonstrates a three-agent agentic workflow using [Strands Agents](https://github.com/strands-agents/docs), monitored with [TraceCtrl](https://tracectrl.io).

A **Researcher**, **Analyst**, and **Writer** agent work in sequence to research a topic or fact-check a claim, with every agent call and tool use visible in the TraceCtrl UI.

## Prerequisites

- Python 3.10+ **or** [uv](https://docs.astral.sh/uv/getting-started/installation/) (either works — pick whichever you have)
- [Google AI Studio API key](https://aistudio.google.com/apikey)
- TraceCtrl running locally (OTLP endpoint on port 4317)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/tracectrl/tracectrl-bootcamp-examples.git
cd tracectrl-bootcamp-examples
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
GOOGLE_API_KEY=your_google_ai_studio_key
GOOGLE_MODEL_ID=gemini-3.1-flash-lite

TRACECTRL_ENDPOINT=http://localhost:4317
TRACECTRL_SERVICE_NAME=agents-workflow
TRACECTRL_ENVIRONMENT=demo
```

Replace `your_google_ai_studio_key` with your API key from [Google AI Studio](https://aistudio.google.com/apikey) and set `GOOGLE_MODEL_ID` to the model you want to use (e.g. `gemini-3.1-flash-lite`, `gemini-2.0-flash`).

### 3. Make the script executable

```bash
chmod +x run_agents_workflow.sh run_agents_workflow_uv.sh
```

## Running the Example

### 1. Ensure TraceCtrl is running

Make sure your TraceCtrl instance is up and accepting traces on port 4317 before proceeding.

### 2. Execute the script

Pick the runner that matches your environment — both create a local virtual environment and install dependencies on first run, then reuse it on subsequent runs.

**With pip (Python 3.10+):**

```bash
bash run_agents_workflow.sh
```

**With [uv](https://docs.astral.sh/uv/getting-started/installation/):**

```bash
bash run_agents_workflow_uv.sh
```

The two runners use separate venv directories (`venv/` for pip, `.venv/` for uv) so they don't conflict if you try both.

### 3. Enter your question

At the prompt, enter a research question or a claim to fact-check:

```
> What are quantum computers?
> Lemon cures cancer
> Tuesday comes before Monday in the week
```

Type `exit` to quit.

### 4. View the Topology

Open the TraceCtrl UI and navigate to the **Topology** view to see the full agent workflow — each agent, tool call, and LLM invocation traced in real time.

![Topology](topology.png)
