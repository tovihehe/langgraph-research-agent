"""State definitions.

State is the interface between the graph and end user as well as the
data model used internally by the graph.
"""
import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, List, Optional, Dict
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

@dataclass(kw_only=True)
class State:
    """Input state defines the interface between the graph and the user (external API)."""

    topic: str
    "The topic for which the agent is tasked to gather information."

    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)
    """Messages track the primary execution state of the agent."""

    loop_count: int = field(default=0)
    "A counter to track the number of loops the agent has executed."

    urls: List[str] = field(default_factory=list)
    "A list of extracted URLs to be processed by the agent."

    extracted_info: Dict[str, dict[str, Any]] = field(default_factory=dict)
    "A dictionary mapping each processed URL to its extracted information."

    synthesized_info: Optional[dict[str, Any]] = field(default=None)
    "The final synthesized information after processing extracted data."

    # references: Optional[List[str]] = field(default=None)
    "A list of references used to generate the synthesized information."

    # justification: Optional[str] = field(default=None)
    "Justification for the synthesized information."

    validation_result: Optional[dict[str, Any]] = field(default=None)
    "Stores the validation results to determine if additional searches are needed."
    
    is_satisfactory: bool = field(default=True)
    "Stores if the response is satisfactory or not"

    previous_info: Optional[dict[str, Any]] = field(default=None)
    "The previous synthesized information after processing extracted data."