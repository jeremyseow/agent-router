import os
import logfire
import asyncpg
import yaml
import pandas as pd
import io
from pypdf import PdfReader
from google import genai
from core.config import settings
from core.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, EMBEDDING_MODEL

def extract_text_from_bytes(filename: str, content: bytes) -> str:
    """Extracts text from various file formats provided as bytes."""
    _, ext = os.path.splitext(filename.lower())
    
    try:
        if ext == '.md':
            return content.decode("utf-8")
        elif ext == '.pdf':
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif ext == '.csv':
            df = pd.read_csv(io.BytesIO(content))
            return df.to_string()
        elif ext in ('.yaml', '.yml'):
            data = yaml.safe_load(content.decode("utf-8"))
            return yaml.dump(data, default_flow_style=False)
        else:
            logfire.warning(f"Unsupported file format: {ext} for {filename}")
            return ""
    except Exception as e:
        logfire.error(f"Failed to extract text from {filename}: {e}")
        return ""

async def document_exists(conn: asyncpg.Connection, document_name: str) -> bool:
    """Checks if a document has already been indexed in the knowledge base."""
    row = await conn.fetchrow(
        "SELECT 1 FROM knowledge_chunks WHERE document_name = $1 LIMIT 1",
        document_name
    )
    return row is not None

async def delete_document(conn: asyncpg.Connection, document_name: str):
    """Deletes all chunks associated with a specific document."""
    logfire.info(f"Removing existing index for: {document_name}")
    await conn.execute(
        "DELETE FROM knowledge_chunks WHERE document_name = $1",
        document_name
    )

async def ingest_document_content(
    pool: asyncpg.Pool, 
    document_name: str, 
    content_bytes: bytes, 
    overwrite: bool = False
) -> dict:
    """
    Processes document bytes, chunks them, embeds them, and saves to PG.
    Returns a status dict.
    """
    async with pool.acquire() as conn:
        exists = await document_exists(conn, document_name)
        
        if exists:
            if not overwrite:
                logfire.info(f"Skipping {document_name} (already indexed).")
                return {"status": "skipped", "document": document_name}
            else:
                await delete_document(conn, document_name)

        logfire.info(f"Ingesting document content: {document_name}")
        
        text = extract_text_from_bytes(document_name, content_bytes)
        if not text.strip():
            logfire.warning(f"No text extracted from {document_name}, skipping.")
            return {"status": "error", "message": "No text extracted", "document": document_name}

        # Simple chunking logic
        chunks = []
        for i in range(0, len(text), DEFAULT_CHUNK_SIZE - DEFAULT_CHUNK_OVERLAP):
            chunks.append(text[i : i + DEFAULT_CHUNK_SIZE])

        client = genai.Client()
        
        for i, chunk in enumerate(chunks):
            logfire.info(f"Processing chunk {i+1}/{len(chunks)} of {document_name}")
            
            # 1. Embed the chunk
            try:
                embedding_response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=chunk,
                    config={
                        'output_dimensionality': 768
                    }
                )
                vector = embedding_response.embeddings[0].values
            except Exception as e:
                logfire.error(f"Embedding failed for chunk {i} of {document_name}: {e}")
                continue
            
            # 2. Save to database
            await conn.execute(
                """
                INSERT INTO knowledge_chunks (document_name, content, embedding, metadata)
                VALUES ($1, $2, $3, $4::jsonb)
                """,
                document_name,
                chunk,
                vector,
                '{"index": ' + str(i) + '}'
            )
            
    return {"status": "success", "document": document_name, "chunks": len(chunks)}
