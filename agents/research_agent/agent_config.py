from typing import Dict
from pydantic import Field
from typing import Optional
from langchain_core.runnables import RunnableConfig, ensure_config
from dataclasses import dataclass, fields


@dataclass(kw_only=True)
class AgentConfig:
    """Configuration for the agent."""
    llm_provider: str = Field(
        default="openai",
        description="LLM provider (e.g., 'google', 'openai', 'anthropic', 'aws')"
    )
    llm_name: str = Field(
        default="gpt-4o-mini",
        description="Name of the LLM model"
    )
    llm_temperature: float = Field(
        default=0.0,
        description="LLM temperature"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model"
    )
    prompt_paths: Dict[str, str] = Field(
        default_factory=dict,
        description='Paths of the Agent'
    )
    max_search_results: int = Field(
        default=5,
        description="Maximum number of search results"
    )
    max_loops: int = Field(
        default=1,
        description="Maximum number of loops"
    )
    
    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "AgentConfig":
        """Load configuration w/ defaults for the given invocation."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
    
# Example of how to use it
if __name__ == "__main__":
    config = AgentConfig.load_config("config/research_agent_config.yaml")
    runnable_config = RunnableConfig(configurable={"llm_provider": "google"})
    agent_config = AgentConfig.from_runnable_config(runnable_config)
    print(agent_config)

