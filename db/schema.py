import logfire
from db.session import get_db_connection

async def initialize_schema():
    """Creates the initial database schema if it doesn't exist."""
    logfire.info("Initializing database schema...")
    async with get_db_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_configs (
                id SERIAL PRIMARY KEY,
                agent_name VARCHAR(255) UNIQUE NOT NULL,
                system_prompt TEXT NOT NULL,
                enabled_tools TEXT[] NOT NULL DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insert default agent configurations if they don't exist
        await conn.execute("""
            INSERT INTO agent_configs (agent_name, system_prompt, enabled_tools)
            VALUES 
                ('pm', 'You are an expert Project Manager. You break down tasks into subtasks and ensure all engineering output meets the user''s goals.', '{"read_fs", "write_fs"}'),
                ('engineer', 'You are an expert Software Engineer. You write python code, test, and perform technical execution.', '{"read_fs", "write_fs", "api_get", "api_post"}'),
                ('financial_analyst', 'You are an expert Financial Analyst. You can request market data via APIs and read financial docs.', '{"read_fs", "api_get"}')
            ON CONFLICT (agent_name) DO NOTHING;
        """)
        logfire.info("Database schema initialized successfully.")
