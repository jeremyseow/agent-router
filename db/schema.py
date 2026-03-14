import logfire
from db.session import get_db_connection

import asyncpg

# TODO: consider using a proper migration tool in the future.
async def initialize_schema(pool: asyncpg.Pool):
    """Creates the initial database schema if it doesn't exist."""
    logfire.info("Initializing database schema...")
    async with get_db_connection(pool) as conn:
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_configs (
                id SERIAL PRIMARY KEY,
                agent_name VARCHAR(255) UNIQUE NOT NULL,
                role_prompt TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                enabled_tools TEXT[] NOT NULL DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                summary TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id SERIAL PRIMARY KEY,
                document_name VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                embedding vector(768),
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create an index for faster vector searches
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding 
            ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_jobs (
                job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                filename VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert default agent configurations if they don't exist...
        await conn.execute("""
            INSERT INTO agent_configs (agent_name, role_prompt, system_prompt, enabled_tools)
            VALUES 
                ('pm', 'Project Manager who breaks down tasks and orchestrates engineering output.', 'You are an expert Project Manager. You break down tasks into subtasks and ensure all engineering output meets the user''s goals.', '{"read_fs", "write_fs"}'),
                ('engineer', 'Software Engineer who writes code, tests, and executes technical tasks.', 'You are an expert Software Engineer. You write python code, test, and perform technical execution.', '{"read_fs", "write_fs", "api_get", "api_post"}'),
                ('financial_analyst', 'Financial Analyst who queries market data and analyzes stocks.', 'You are an expert Financial Analyst. You can request market data via APIs and read financial docs.', '{"read_fs", "api_get"}'),
                ('research_assistant', 'Research Assistant who searches the web to find accurate, up-to-date information.', 'You are an expert Research Assistant. You use the web search tool to find the most accurate and up-to-date information, filter the noise, and summarize the findings concisely for the user.', '{"web_search"}'),
                ('librarian', 'Specialized Knowledge Base Agent (Librarian) who manages and retrieves information from internal project documents.', 'You are an expert Librarian. You have access to the internal knowledge base which contains documentation, architecture details, and technical notes. ALWAYS use the `search_knowledge_base` tool to answer questions about the system''s history, design, architecture, or internal specifications. Do not rely on your own internal knowledge if the information might be in the documents.', '{"search_knowledge_base"}')
            ON CONFLICT (agent_name) DO UPDATE SET 
                role_prompt = EXCLUDED.role_prompt,
                system_prompt = EXCLUDED.system_prompt,
                enabled_tools = EXCLUDED.enabled_tools;
        """)
        logfire.info("Database schema initialized successfully.")
