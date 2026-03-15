import logfire
from google import genai
from google.genai import types
from pydantic_ai import RunContext
from models.dependencies import RouterDependencies
from core.constants import EMBEDDING_MODEL
import numpy as np

async def search_knowledge_base(ctx: RunContext[RouterDependencies], query: str) -> str:
    """
    Searches the internal knowledge base for technical documentation related to various domains such as software engineering, financial analysis, and more.
    Use this tool to answer questions on topics such as distributed systems, software architecture, financial modeling, and more.
    """
    logfire.info(f"Searching knowledge base for: {query}")
    
    # Generate embedding for the query
    client = genai.Client()
    embedding_response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config={'output_dimensionality': 768}
    )
    query_vector = embedding_response.embeddings[0].values
    
    # Search DB
    pool = ctx.deps.db_pool
    async with pool.acquire() as conn:
        # TODO: move queries to the repository layer
        rows = await conn.fetch(
            """
            SELECT content, document_name, metadata
            FROM knowledge_chunks
            ORDER BY embedding <=> $1::vector
            LIMIT 5
            """,
            query_vector
        )
        
    if not rows:
        return "No relevant information found in the knowledge base."
        
    # Format the results
    results = []
    for row in rows:
        source = f"Source: {row['document_name']}"
        results.append(f"--- {source} ---\n{row['content']}")
        
    return "\n\n".join(results)
