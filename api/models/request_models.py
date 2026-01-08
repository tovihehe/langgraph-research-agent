from pydantic import BaseModel, Field
from typing import Optional, List

class InitAgentRequest(BaseModel):
    use_guardrails: Optional[bool] = True

class AskAgentRequest(BaseModel):
    question: str
