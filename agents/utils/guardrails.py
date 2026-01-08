import json, yaml
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from interfaces.llm_interface_2 import LLMInterface
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

class GuardrailsConfig(BaseModel):
    llm_provider: str = Field(default="openai", description="LLM provider (e.g., 'google', 'openai', 'anthropic', 'aws')")
    llm_name: str = Field(default="gpt-4o", description="Name of the LLM model")
    llm_temperature: float = Field(default=0.0, description="LLM temperature")
    embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")
    guardrails_prompt_path: str = Field(default="guardrails_prompt.txt", description="Path to the security prompt file")

class Risks(BaseModel):
    pii_detection: float = Field(description="Puntaje de detección de PII (0-1).", ge=0, le=1)
    prompt_injection: float = Field(description="Puntaje de riesgo de inyección de prompts (0-1).", ge=0, le=1)
    security_risks: float = Field(description="Puntaje de riesgos de seguridad generales (0-1).", ge=0, le=1)
    safe_text: Optional[str] = Field(description="Versión reescrita del texto o mensaje de advertencia.")

class Guardrails:
    def __init__(self, config_path: str):
        self.config = self.load_security_config(config_path)
        self.llm = LLMInterface(self.config).get_llm()
        self.output_parser = PydanticOutputParser(pydantic_object=Risks)

        with open(self.config.guardrails_prompt_path, "r", encoding="utf-8") as f:
            self.security_prompt = f.read()
        
        self.security_prompt = PromptTemplate(
            template=self.security_prompt,
            input_variables=["text"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions}
        )
        self.chain = self.security_prompt | self.llm | self.output_parser

    def load_security_config(self, config_path: str) -> GuardrailsConfig:
        """Loads the llm configuration from a YAML file."""
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return GuardrailsConfig(**config_data)

    def check_malicious_question(self, question: str) -> str:
        """Detects the security attempt in the given text."""
        attempt = self.detect_attempt(question)
        if attempt["safe_text"] == "No se permiten operaciones que comprometan la seguridad del sistema.":
            return True, attempt["safe_text"]

        return False, question

    def detect_attempt(self, text: str) -> Dict[str, Any]:
        """Detects security risks in the given text."""
        try:
            result = self.chain.invoke(text)
            if isinstance(result, Risks):
                scores = dict(result) 
            else:
                scores = json.loads(result.strip())

            validated_scores = Risks(**scores)

            overall_score = sum([
                validated_scores.pii_detection,
                validated_scores.prompt_injection,
                validated_scores.security_risks,
            ]) / 5

            if validated_scores.safe_text in (None, "", "null"):
                validated_scores.safe_text = text

            return {
                "text": text,
                "score": overall_score,
                "detailed_scores": dict(validated_scores),
                "safe_text": validated_scores.safe_text
            }

        except Exception as e:
            return {"text": text, "response": "error", "reason": str(e)}

if __name__ == "__main__":
    detector = Guardrails("")
    query = ""
    result = detector.detect_attempt(query)
    print(result)