# Lessons Learned & Architecture Gotchas

As per our self-annealing directives, this document tracks framework quirks, limitations, and the root causes & fixes discovered during development.

## Pydantic AI
### 1. `GeminiModel` Initialization
- **Issue**: Initializing `GeminiModel(..., api_key=...)` threw an unexpected keyword argument `api_key` error.
- **Root Cause & Fix**: Pydantic AI's Gemini integration explicitly looks for the environment variable `GOOGLE_API_KEY` or a `GoogleProvider` instance rather than a direct string kwarg. We fixed this by manually shoving `settings.gemini_api_key` into `os.environ["GOOGLE_API_KEY"]` before agent initialization if present.

### 2. Structured Outputs Kwarg change
- **Issue**: `Agent(..., result_type=...)` threw an unexpected keyword argument `result_type` error.
- **Root Cause & Fix**: Recent versions of `pydantic-ai` refactored the signature, deprecating `result_type` in favour of `output_type`. We must use `output_type=ModelClass` for structured outputs now.

### 3. AgentRunResult Data Attribute
- **Issue**: `AgentRunResult` object threw an `AttributeError` for no attribute `.data`.
- **Root Cause & Fix**: The Pydantic AI API changed how agent outputs are accessed on the result object backwards unpredictably in new releases. The attribute is named `.output` instead of `.data`. Updated `main.py` router mapping.

## Logfire Observability
### 1. FastAPI Instrumentation Dependencies
- **Issue**: Calling `logfire.instrument_fastapi(app)` fails with a `ModuleNotFoundError` for `opentelemetry.instrumentation.asgi` if you only installed the base `logfire` package.
- **Root Cause & Fix**: Logfire relies on OpenTelemetry extras for FastAPI. We must ensure the `[fastapi]` extra is installed via `uv add "logfire[fastapi]"`.
