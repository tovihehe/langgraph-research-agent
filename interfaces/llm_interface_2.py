from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()
logger = logging.getLogger(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")

class LLMInterface:
    """Utility class for managing language chain components."""
    
    def __init__(self, config):
        self.config = config

    def get_llm(self, llm_type="default"):
        """Returns the appropriate LLM based on the configuration and llm_type."""

        if llm_type == "cypher_llm":
            print('llm provider: ', self.config.cypher_llm_provider)
            print('llm name: ', self.config.cypher_llm_name)
            print('llm temperature: ', self.config.cypher_llm_temperature)    
            provider = self.config.cypher_llm_provider
            name = self.config.cypher_llm_name
            temperature = self.config.cypher_llm_temperature
        elif llm_type == "qa_llm":
            print('llm provider: ', self.config.qa_llm_provider)
            print('llm name: ', self.config.qa_llm_name)
            print('llm temperature: ', self.config.qa_llm_temperature)          
            provider = self.config.qa_llm_provider
            name = self.config.qa_llm_name
            temperature = self.config.qa_llm_temperature
        elif llm_type == "reformulate_llm":
            print('llm provider: ', self.config.reformulate_llm_provider)
            print('llm name: ', self.config.reformulate_llm_name)
            print('llm temperature: ', self.config.reformulate_llm_temperature)            
            provider = self.config.reformulate_llm_provider
            name = self.config.reformulate_llm_name
            temperature = self.config.reformulate_llm_temperature
        else:
            print('llm provider: ', self.config.llm_provider)
            print('llm name: ', self.config.llm_name)
            print('llm temperature: ', self.config.llm_temperature)
            provider = self.config.llm_provider
            name = self.config.llm_name
            temperature = self.config.llm_temperature

        if provider == "openai":
            return ChatOpenAI(temperature=temperature, model=name, openai_api_key=openai_api_key)
        else:
            raise ValueError(f"Proveedor LLM no soportado: {provider}")
        
    def get_embeddings(self):
        """Returns the OpenAI embeddings object."""
        print('embedding_model: ', self.config.embedding_model)
        return OpenAIEmbeddings(api_key=openai_api_key, model=self.config.embedding_model)