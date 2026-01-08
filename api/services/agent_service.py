import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from dotenv import load_dotenv
from agent.main import main

class Agent:
    def __init__(self):
        self.initialized = False
        self.config = None
        self.sql_agent = None

    def initialize(self,
                   session_id: str = None,
                   use_guardrails: bool = True,
                   ):

        if session_id is None:
            session_id = str(uuid.uuid4())
        # Configure SQL agent
        load_dotenv('api/.env', override=True)
        agent_config_path = os.getenv('AGENT_CONFIG_PATH')
        guardrails_config_path = os.getenv('GUARDRAILS_CONFIG_PATH')
        self.agent = main(
                            agent_config_path, 
                            guardrails_config_path, 
                            session_id=session_id,
        )

        self.initialized = True
        return f"Agente inicializado correctamente para el usuario"

    def ask(self, question: str):
        if not self.initialized:
            raise ValueError("El agente no ha sido inicializado.")
        if not question:
            raise ValueError("La pregunta no puede estar vacía.")
        # Aquí iría la lógica de procesamiento de la pregunta
        result = self.sql_agent.ask(question)

        return result


