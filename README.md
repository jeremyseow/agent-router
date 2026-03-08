# Agent Router

An autonomous conversational AI middleware capable of scaling specialized workers dynamically. Using **Pydantic AI**, **FastAPI**, and a **PostgreSQL** persistence layer, the application accepts user input, leverages a "Router Agent" to perform intent classification, and delegates complex specialized tasks to configurable "Worker Agents" running in parallel or sequentially.

---

## 🏗 High-Level Architecture

The Agent Router is designed around a decoupled, database-driven **Multi-Agent Orchestration Graph**. Instead of hardcoding branching logic into the API endpoints, the FastAPI server cleanly passes the user's message to a central **Router Agent**. This Router Agent acts as an unrestricted conversational orchestrator, natively using Pydantic AI's dynamic tool-calling functionality to summon, parallelize, and synthesize data from multiple specialized sub-agents.

The architecture models a 3-layer system:
- **Application Layer**: External requests through the FastAPI REST endpoint logic.
- **Orchestration Layer**: A Router Agent evaluating intent and wielding a proxy `delegate_to_worker` tool to programmatically spawn isolated, context-aware worker instances that are implemented as tools.
- **Execution Layer**: Specific roles (e.g. Project Manager, Engineer, Research Assistant) instantiated dynamically at startup from configurations stored in the database. Tools (like Local File I/O or Web Search) are injected into these workers strictly based on these configurations.

```mermaid
graph TD
    User([User Client]) <--> API[FastAPI Web/Rest API]
    
    subgraph Core
        API
        Config[Pydantic Settings]
        Obs[Logfire Observability]
    end

    subgraph Orchestration
        Router[Router Agent]
    end

    subgraph Execution Layer
        direction LR
        Registry((Worker Registry))
        PM[PM Agent]
        Eng[Engineer Agent]
        FA[Financial Analyst Agent]
    end

    subgraph Database Layer
        ConfigDB[(PostgreSQL)]
    end

    API -->|Prompt + Context| Router
    Config --> API
    Obs -.-> API
    Obs -.-> Router
    Obs -.-> ExecutionLayer
    
    Router -->|Determines Target| Registry
    Registry --> PM
    Registry --> Eng
    Registry --> FA
    
    ConfigDB -->|Loads Policies & Tools| Registry
    Router -.-> ConfigDB
```

## 🔄 Sequence Flows

**Standard Task Delegation Flow**
```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant Auth as Config/DB
    participant Router as Router Agent
    participant Worker as Worker Agent (e.g., PM, Engineer)
    participant Model as LLM

    User->>API: POST /chat {message, session}
    API->>Auth: Load active session & context
    API->>Router: process_message(context)
    Router->>Model: Evaluate intent & routing
    Model-->>Router: Action: Delegate to Worker
    Router->>Worker: Dispatch task description
    Worker->>Auth: Fetch Agent config/prompt (if dynamic)
    Worker->>Model: Execute task solving (loop)
    Model-->>Worker: Final Output
    Worker-->>Router: Task Result
    Router-->>API: Format & reply
    API-->>User: Response payload
```

## ⚖️ Design Choices & Trade-Offs

| Decision | Pros | Cons |
| :--- | :--- | :--- |
| **Pydantic AI over LangChain** | Typesafe, Pythonic structured outputs natively out of the box with zero-overhead configuration. Dynamic dependency injection is first-class. | Nascent ecosystem, relatively sparse tooling registry, and occasional breaking API output changes (e.g., `RunResult.data` vs `.output`). |
| **PostgreSQL Driven Agents** | Decouples application restart logic from runtime role assignment. Highly scalable. Allows adding new agents to the swarm without code deployments. | Demands robust local database environments (Docker required even locally). Slows down boot times slightly. |
| **LLM Orchestration vs Hardcoded Graphs** | The Router LLM natively constructs its own DAG execution graph using Pydantic tool arrays. It can run tools in parallel or sequentially based entirely on natural language dependencies. | Loss of strict procedural control; relies heavily on the reasoning capability of the root Orchestrator model (Gemini 2.5 Flash minimum required). |
| **Strict Tool Segregation (Gemini Limitation)** | Gemini natively prevents agents from using Google Grounding Tools (e.g., `WebSearchTool`) alongside Custom Function Tools (`write_fs`) on the same agent instance. The orchestration model naturally solves this by tasking the Researcher to search, and the Engineer to write. | Requires careful allocation of tools in the database schema; an agent cannot be a "jack of all trades" if it utilizes native web search integrations. |
| **Pydantic Settings & `.env`** | Industry standard, inherently typesafe validation for credentials immediately avoiding runtime explosions. | Difficult debugging if variable precedence overlaps with host OS variables unknowingly. |

## 🧪 Testing Approach (Agentic Evaluation)

Because LLMs are non-deterministic, testing requires a multi-layered strategy:
1. **Layer 1 (Deterministic)**: Standard `pytest` for unit tests.
2. **Layer 2 (Behavioral)**: Utilizing Pydantic AI's `FunctionModel` and `TestModel` to simulate agent routing logic, tool calls, and agent responses without actually calling the LLMs.
3. **Layer 3 (LLM as a Judge)**: Utilizing Pydantic AI's `Evaluator` and LLMs to run critical scenarios and score responses programmatically based on accuracy and completeness.

## 📁 Project Structure

```text
agent-router/
├── .env                  # Secrets and DB credentials
├── .tmp/                 # Scraped data & intermediate LLM data (Ignored)
├── agent_output/         # Safe restrict sandbox for Worker Agent File Generation
├── docker-compose.yml    # Database infrastructure (Postgres & PGAdmin)
├── main.py               # FastAPI application, startup logic & REST endpoints
├── pyproject.toml        # uv Dependency configuration
│
├── core/
│   ├── config.py         # Global settings loading
│   └── observability.py  # Logfire Configuration
│
├── db/
│   ├── agent_config.py   # Database mapping and agent configurations 
│   ├── schema.py         # Table definition and initial setup population
│   └── session.py        # AsyncPG connection pools
│
├── models/
│   └── api.py            # FastAPI Request/Response structures
│
├── tests/
│   ├── unit/             # Layer 1: Deterministic pure Python testing
│   ├── integration/      # Layer 2: API/DB/LLM Behavioral Contract wiring tests
│   └── e2e/              # Layer 3: End-to-end HTTP tests (future)
│
├── agents/
│   ├── router.py         # Dynamic routing logic parsing LLM targets
│   └── workers.py        # Abstract dynamically-initialized workers
│
└── tools/
    ├── api_tools.py      # HTTP helper functions
    ├── fs_tools.py       # Sandbox Local File I/O
    └── registry.py       # Pointers translating DB strings to Py Functions
```

## 🚀 Quick Start Guide

**1. Prerequisites**
- Install `uv` for python dependencies.
- Install Docker for the database containers.
- Have a Gemini API key.

**2. Setup Environment**
Duplicate the `.env.template` into a local `.env` file and insert your credentials.
```bash
cp .env.template .env
```
_Ensure `GEMINI_API_KEY` is populated._

**3. Start the Database**
Launch the PostgreSQL engine in the background:
```bash
docker-compose up -d
```

**4. Run the Application**
Start the FastAPI server (using `uv run` will automatically install the project's dependencies if not yet synced):
```bash
uv run uvicorn main:app --reload
```
_On the first launch, the `lifespan` event will automatically populate your PostgreSQL database with the default Agent Roles and Tools via `db/schema.py`._

**5. Exploring API**
Navigate to the Swagger UI available at:
`http://localhost:8000/docs`
You can post a request directly to the `/chat` route to see the Router automatically decide whether to handle it or delegate it to a Worker Agent!

**6. Running Tests**
Execute the pytest suite to validate the deterministic and behavioral layers of the agent:
```bash
uv run pytest -v tests/
```
