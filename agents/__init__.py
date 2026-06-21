import os
import litellm
from crewai import LLM
from fin_agent.config.settings import ANTHROPIC_API_KEY, OPENAI_API_KEY

_original_completion = litellm.completion
def patched_completion(*args, **kwargs):
    if "messages" in kwargs:
        for msg in kwargs["messages"]:
            if "cache_breakpoint" in msg:
                del msg["cache_breakpoint"]
    return _original_completion(*args, **kwargs)
litellm.completion = patched_completion


def get_llm():
    if ANTHROPIC_API_KEY:
        return LLM(
            model="anthropic/claude-3-5-sonnet-20241022",
            api_key=ANTHROPIC_API_KEY
        )
    elif OPENAI_API_KEY:
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        api_base = os.getenv("OPENAI_API_BASE", "")
        
        # Litellm workaround for Groq to avoid cache_breakpoint error on OpenAI compatibility endpoint
        if "groq" in api_base.lower() or "groq" in model_name.lower():
            if model_name.startswith("openai/"):
                model_name = model_name.split("openai/")[1]
            return LLM(
                model=f"groq/{model_name}",
                api_key=OPENAI_API_KEY
            )
        else:
            return LLM(
                model=model_name,
                api_key=OPENAI_API_KEY,
                base_url=api_base if api_base else None
            )
    else:
        raise ValueError("Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set. Please configure at least one in the .env file.")
