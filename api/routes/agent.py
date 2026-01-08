import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, HTTPException, Depends
from api.models.request_models import AskAgentRequest
from api.models.response_models import AgentResponse, QuestionResponse
from api.services.agent_service import Agent
from api.middleware.security import get_current_user
# Change agent_name with your specific agent 
router = APIRouter(prefix="/agent_name")
agent = Agent()

@router.get("/")
async def root():
    return {"message": "API de SQL Agent funcionando correctamente"}

@router.post("/initialize", response_model=AgentResponse)
async def initialize_agent( current_user=Depends(get_current_user)):
    """
    Inicializa el agente de IA con los parámetros proporcionados.
    """
    try:     
        agent.initialize() 
        return {"status": "success",
                "response": 'Agent initialized successfully'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ask", response_model=QuestionResponse)
async def ask_agent(request: AskAgentRequest, current_user=Depends(get_current_user)):
    """
    Envía una pregunta al agente de IA y devuelve su respuesta.
    """
    try:
        response = agent.ask(str(request.question))
        return {
            "status": "success", 
            "response": response
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
