# TraceCtrl Bootcamp Examples                                                                                                                                                        
                                                                                                                    
  Pre-instrumented [Strands Agents](https://github.com/strands-agents/docs) workflows for the [TraceCtrl bootcamp](https://docs.tracectrl.io/bootcamp/strands-guide). Both examples run
   on a free Google AI Studio API key and emit OpenTelemetry traces to a local TraceCtrl stack.                                                    
                                                                                                                                                                                       
  ## Examples                                                                                                                                                                        
                                         
  | Directory | Topology | What it demos |                                                                                                                                             
  |-----------|----------|---------------|                                                                                                                                             
  | [`research_workflow_example/`](./research_workflow_example) | Researcher → Analyst → Writer (3 agents, 1 tool) | Sequential hand-off via tool calls; web research with             
  `http_request`; fact-checking |                                                                                                                                                      
  | [`teacher_assistants_workflow_example/`](./teacher_assistants_workflow_example) | TeachAssist orchestrator → 4 subject specialists | Classifier-style routing; one orchestrator    
  delegates to MathWizard, EnglishMaster, LanguageAssistant or GeneralAssist |                                                                                 
                                                                                                                                                                                     
  Each example is self-contained — see its README for setup and run instructions.                                                                                                      
                                                                                                                                                                                     
  ## Prerequisites (shared)                                                                                                                                                            
                                                                                                                                                                                     
  - **Python 3.10+** **or** [**uv**](https://docs.astral.sh/uv/getting-started/installation/) — each example ships both a `run_agents_workflow.sh` (pip) and `run_agents_workflow_uv.sh` (uv) runner; pick whichever you have.
  - **Google AI Studio API key** — free, no credit card. Get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
  - **TraceCtrl stack running locally** with the OTLP collector accepting traces on `:4317`. Follow [Part 2 of the bootcamp                                                            
  guide](https://docs.tracectrl.io/bootcamp/strands-guide#part-2-start-the-tracectrl-stack).                                                                                           
  - **TraceCtrl SDK cloned locally.** Both examples install the SDK from a local path (it's not yet on PyPI). The `run_agents_workflow.sh` script in each example takes a              
  `TRACECTRL_SDK` path you fill in.                                                                                                                                                    
                                                                                                                    
  ## Models                                                                                                                                                                            
                                                                                                                    
  The examples default to `gemini-3.1-flash-lite` (preview). `gemini-2.5-flash` also works and has comparable free-tier headroom — swap by setting `GOOGLE_MODEL_ID` in the example's  
  `.env`.
                                                                                                                                                                                       
  ## What you'll see in TraceCtrl                                                                                   
                                         
  After running either example with a few prompts:                                                                                                                                     
   
  - **Sessions** — one row per agent run, expanding to a trace tree of agent → LLM → tool spans                                                                                        
  - **Topology** — auto-built from span relationships; one agent node per `tag_agent(...)` call, edges labelled `delegates` / `uses`
  - **Agents** — every agent registered with its name, role, and recent activity                                                                                                       
                                                                                                                                                                                       
  ## Troubleshooting                                                                                                                                                                   
                                                                                                                                                                                       
  - **No traces appearing.** Confirm the TraceCtrl OTel collector is up: `curl http://localhost:4317` should fail with a gRPC error rather than connection-refused. Check              
  `TRACECTRL_ENDPOINT` in your `.env`.   
  - **Rate-limited mid-session.** Free-tier Gemini caps are generous but not infinite — swap `GOOGLE_MODEL_ID` in `.env` to a different flash variant and rerun.                       
  - **`run_agents_workflow.sh` fails on SDK install.** The script looks for `tracectrl/` and `tracectrl-instrumentation-strands/` inside the path you set as `TRACECTRL_SDK`. Make sure
   that path points at the SDK monorepo root, not one level deeper.  
