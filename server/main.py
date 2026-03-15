import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.observability import setup_observability
from db.session import init_db_pool
from db.schema import initialize_schema
from agents.workers import init_workers
from api.routers.chat import router as chat_router
from api.routers.images import router as images_router
from api.routers.ingestion import router as ingestion_router

# Setup logfire immediately
setup_observability()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logfire.info("Starting up Agent Router API...")
    pool = await init_db_pool()
    await initialize_schema(pool)
    registry = await init_workers(pool)
    
    # Inject application state globally down to routers
    app.state.pool = pool
    app.state.worker_registry = registry
    yield
    
    # Shutdown actions
    logfire.info("Shutting down Agent Router API...")
    await pool.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)
logfire.instrument_fastapi(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the external routers
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(images_router, prefix="/images", tags=["Images"])
app.include_router(ingestion_router, prefix="/kb", tags=["Knowledge Base"])
