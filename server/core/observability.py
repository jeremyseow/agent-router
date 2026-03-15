import logfire
from core.config import settings

def setup_observability():
    """Configures Logfire for observability and logging."""
    if settings.logfire_token:
        # Configure to send data to Logfire cloud if token is present
        logfire.configure(token=settings.logfire_token, environment=settings.app_env)
        logfire.instrument_pydantic_ai()
        logfire.info("Logfire configured to send logs to cloud.")
    else:
        # Fallback to local console mode
        logfire.configure(send_to_logfire=False)
        logfire.info("Logfire running in local console-only mode.")
