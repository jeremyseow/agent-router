import logfire
from pydantic_ai import Agent, RunContext

summarizer_agent = Agent('gemini-2.5-flash', defer_model_check=True)

@summarizer_agent.system_prompt
async def get_system_prompt(ctx: RunContext) -> str:
    return (
        "You are an expert system-level Summarization Agent.\n"
        "Your sole job is to read raw conversational histories (which include user requests, tool calls, and agent responses) "
        "and compress them into a crystal-clear, highly dense summary document.\n"
        "You must retain all crucial facts, decisions, goals, and context, while discarding redundant verbosity.\n"
        "Your output should be a straightforward narrative summary of the current state of the task or interaction, "
        "without greetings or pleasantries, as your exact output will be fed directly back into an AI Router to serve as its memory for the next turn."
    )
