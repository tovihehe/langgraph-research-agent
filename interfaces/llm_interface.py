from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
import os 
from dotenv import load_dotenv

load_dotenv('.env', override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")

class LLMInterface:
    """Utility class for managing language chain components."""
    
    def __init__(self, config):
        self.config = config

    def get_llm(self) -> Optional[BaseChatModel]:
        """Initialize the configured language model."""

        llm_name = self.config.llm_name
        llm_provider = self.config.llm_provider

        return init_chat_model(llm_name, model_provider=llm_provider, api_key=openai_api_key)
