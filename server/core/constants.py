from enum import Enum

# Knowledge Base Constants
MAX_INGEST_FILES = 5
SUPPORTED_INGEST_EXTENSIONS = {".md", ".pdf", ".csv", ".yaml", ".yml"}

class IngestionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Text Chunking Constants
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

# AI Model Constants
EMBEDDING_MODEL = 'gemini-embedding-001'
SUMMARY_MODEL = 'gemini-2.5-flash'
ROUTER_MODEL = 'gemini-2.5-flash'
IMAGE_GEN_MODEL = 'gemini-2.5-flash-image'
