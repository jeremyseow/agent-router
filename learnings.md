# Learnings

This document captures key learning points and architectural mechanics discovered during the development of the Agent Router.

## Pydantic AI: Parallel vs Sequential Tool Execution

When an LLM (like Gemini 2.5 Flash) orbits a complex instruction requiring multiple tools (such as delegating tasks to different worker agents), it natively decides between parallel and sequential execution based on the dependencies between the tasks.

### 1. Parallel Execution (Independent Tasks)

**Scenario:** The user asks for two independent actions simultaneously (e.g., "Ask the PM to draft a roadmap, and ask the Engineer to write boilerplate code").
**Mechanism:**
1. The LLM's reasoning engine recognizes the tasks do not rely on each other.
2. It returns a single JSON payload containing an array of multiple `tool_calls` requested at the exact same time:
   ```json
   "tool_calls": [
     {
       "id": "call_1",
       "name": "delegate_to_worker",
       "arguments": {"worker_name": "pm", "task_description": "Draft a backend roadmap."}
     },
     {
       "id": "call_2",
       "name": "delegate_to_worker",
       "arguments": {"worker_name": "engineer", "task_description": "Write boilerplate code."}
     }
   ]
   ```
3. Pydantic AI receives this payload and uses Python's `asyncio.gather()` to launch all the requested `async def` tool functions concurrently on the event loop.
4. The worker agents run their separate network requests simultaneously.
5. Once all async promises resolve, Pydantic AI packages the combined results into a single `tool_results` array and fires a second request back to the Router LLM.
6. The Router synthesizes the parallel outputs and streams the final response.

### 2. Sequential Execution (Dependent Tasks)

**Scenario:** The user asks for tasks that rely on previous outputs (e.g., "Ask the PM to draft a roadmap, and *then* ask the Engineer to write the code for it").
**Mechanism:**
1. The Router LLM understands the semantic constraint (the Engineer needs the roadmap first).
2. It fires a **single** tool call to invoke the PM agent first:
   ```json
   "tool_calls": [
     {
       "id": "call_1",
       "name": "delegate_to_worker",
       "arguments": {"worker_name": "pm", "task_description": "Draft a backend roadmap."}
     }
   ]
   ```
3. The Python tool executes the PM sub-agent, awaits the result, and returns the markdown text back to the Router LLM.
4. The Router LLM receives the roadmap, holds it in context, and *then* fires a **second, subsequent tool call** to the Engineer tool, injecting the PM's completed output into the prompt arguments:
   ```json
   "tool_calls": [
     {
       "id": "call_2",
       "name": "delegate_to_worker",
       "arguments": {"worker_name": "engineer", "task_description": "Based on this roadmap: [PM's roadmap text here], write the code."}
     }
   ]
   ```
5. The Engineer agent spins up, writes the code, and returns the result.
6. The Router synthesizes the final message having completed both dependency-chained steps.

**Key Takeaway:** The orchestration framework does not need manual `if/else` dependency graphs. If the tool definitions and system prompts are clear, the LLM itself dynamically constructs the execution graph (Parallel or DAG) directly via structured function-calling loops!

## Gemini API: Grounding Tools vs Custom Function Tools

While implementing the `research_assistant` agent using Pydantic AI's `WebSearchTool`, we discovered a critical constraint within the Google Gemini API natively: **Gemini does not support combining Built-in Grounding Tools (like Google Search) and Custom Function Tools (like our `write_fs` Python function) on the same Agent instance.**

**The Error:**
If an agent is instantiated with both `builtin_tools=[WebSearchTool()]` and a standard `@agent.tool` decorator, Pydantic AI will crash when communicating with the Gemini API, throwing a restriction error: `Google does not support function tools and built-in tools at the same time.`

**The Solution:**
To bypass this limitation without introducing external third-party search APIs (like Tavily) or switching to an OpenAI backend, we implemented a **Strict Role Segregation Pattern**:
1. The `research_assistant` was stripped of its filesystem writing privileges (`write_fs`). It is now a pure "Search and Summarize" built-in agent configured in the Postgres Database with `array['web_search']`.
2. The orchestrating Router LLM is smart enough to handle the data passing. If a user asks to "Search the web and save the results", the Router will sequentially call `delegate_to_worker("research_assistant")`, extract the summary text, and then pass that payload to `delegate_to_worker("engineer")` to actually write the file to the disk using the custom function tools.
