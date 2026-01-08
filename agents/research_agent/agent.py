import asyncio
import json
import pandas as pd
from typing import Any, Dict, List, Optional, cast
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from agents.utils.prompt_manager import PromptManager
from agents.research_agent.state import State
from agents.tools.scrape_website import extract_notes
from agents.tools.search_webs import search
from agents.tools.get_info_excel import generate_json_schema
from agents.tools.save_info_extracted import ExcelInfoSaver
from interfaces.llm_interface import LLMInterface
from agents.research_agent.agent_config import AgentConfig

class SynthesizedInfo(BaseModel):
    """
    Synthesized information from the extracted data.
    """
    summary: str = Field(
        description="The synthesized information from the extracted data."
    )
    references: List[str] = Field(
        description="The URLs from which the information was extracted."
    )
    justification: str = Field(
        description="Justification of the quality of the synthesized information, specifyng the information missing or not clear."
    )


class InfoIsSatisfactory(BaseModel):
    """
    Validate whether the current extracted info is satisfactory and complete.
    """
    reason: List[str] = Field(
        description="Primero, proporcione un razonamiento de por qué este resultado final es bueno o malo. Debe incluir al menos 3 razones."
    )
    is_satisfactory: bool = Field(
        description="Después de proporcionar su razonamiento, proporcione un valor que indique si el resultado es satisfactorio, TRUE si lo es FALSE si no lo es. FUTURO: Si no lo es, reintentará la investigación."
    )
    new_topic: Optional[str] = Field(
        description="Si el resultado no es satisfactorio, proporcione un topic nuevo que permita buscar la información faltante, siempre indicando el nombre de la empresa y el tema sobre lo que hay que buscar, si no dejalo vacío",
        default=None,
    )

class ResearcherAgent:
    """
    Data enrichment agent that uses a LangGraph workflow to gather and process information.
    Works with a chat model that supports tool calling.
    """
    def __init__(self):
        self.graph = self.graph_building()

    def excel_to_json(self, state: State):
        """Convert the Excel file to a JSON schema."""
        print(f"Converting Excel file to JSON schema")
        excel_path = state.input_excel

        # Read Excel file (pandas handles encoding automatically for Excel)
        df = pd.read_excel(excel_path)

        # Generate JSON schema
        schema = generate_json_schema(df)
        state.extraction_schema = json.dumps(schema, indent=2, ensure_ascii=False)

        return {
            "messages": [AIMessage(content="Structure of initial JSON completed.")],
            "extraction_schema": state.extraction_schema
        }
    
    async def search_urls(self, state: State):
        """Search for URLs related to the topic."""
        print(f"Searching for URLs related to {state.topic}")
        topic = state.topic
        response = await search(topic, self.config)
        urls = [item["url"] for item in response]
        return {
            "messages": [AIMessage(content="Search completed. URLs extracted.")],
            "urls": urls
        }
    
    async def extract_info(self, state: State):
        """Extract information from the URLs."""
        print(f"Extracting information from URLs")
        urls = state.urls
        if not urls:
            return {
                "messages": [AIMessage(content="No valid URLs found.")]
            }
        extraction_tasks = [extract_notes(url, state=state, config=self.config) for url in urls]
        extracted_info = await asyncio.gather(*extraction_tasks)

        # Update the state with the extracted information
        state.extracted_info.update({url: info for url, info in zip(urls, extracted_info)})
        
        # Convert the extracted information into AIMessages
        messages = [AIMessage(content=f"Extracted info from {url}:\n{info}") for url, info in state.extracted_info.items()]

        return {
            "messages": messages
        }


    async def synthesize_info(self, state: State):
        """Synthesize the extracted information into a coherent response."""
        print(f"Synthesizing extracted information")
        if not state.extracted_info:
            return {
                "messages": [AIMessage(content="No extracted information to synthesize.")]
            }
         
        # Get the prompt for the synthesis
        prompt = self.prompt_manager.get_prompt("synthesize")
        if not state.previous_info:
            state.previous_info = ''
        
        prompt = prompt.format(
            topic=state.topic,
            extracted_info=json.dumps(state.extracted_info, indent=2, ensure_ascii=False),
            previous_info=json.dumps(state.previous_info, indent=2, ensure_ascii=False)
        )

        # Call the LLM to synthesize the information
        llm = LLMInterface(self.config).get_llm()
        bound_model = llm.with_structured_output(SynthesizedInfo)
        response = cast(SynthesizedInfo, await bound_model.ainvoke(prompt))
        response = await llm.ainvoke(prompt)
        state.synthesized_info = response.model_dump()
          
        return {
            "messages": [AIMessage(content="Synthesis completed.")],
            "synthesized_info": state.synthesized_info,
        }
 

    async def validate_info(self, state: State):
        """Review if the synthesized information is satisfactory, and if not, generate a new topic to restart the search."""
        print(f"Validating synthesized information")
        if not state.synthesized_info:
            return {
                "messages": [AIMessage(content="No synthesized information to validate.")]
            }
        
        prompt = self.prompt_manager.get_prompt("validate").format(
            topic=state.topic,
            synthesized_info=json.dumps(state.synthesized_info, indent=2, ensure_ascii=False)
        )

        # Call the LLM to validate the synthesized information, see if it's satisfactory
        llm = LLMInterface(self.config).get_llm()
        bound_model = llm.with_structured_output(InfoIsSatisfactory)
        response = cast(InfoIsSatisfactory, await bound_model.ainvoke(prompt))
        state.is_satisfactory = bool(response.is_satisfactory)

        # If the info is satisfactory, return the final response
        if state.is_satisfactory:
            print(f"The info is satisfactory. Research finished.")
            return {
                "messages": [AIMessage(content=f"Research finished")],
                "is_satisfactory": state.is_satisfactory,
            } 
    
        # If the info is not satisfactory, generate a new topic and restart the search
        else:
            print(f"New topic generated: {response.new_topic}. Restarting search.")
            state.topic = response.new_topic
            return {
                "messages": [AIMessage(content=f"New topic generated: {state.topic}. Restarting search.")],
                "is_satisfactory": state.is_satisfactory,
                "topic": state.topic,
                "loop_count": state.loop_count + 1,
                "previous_info": state.synthesized_info,
            }
        
    def save_info(self, state: State):
        """Save the extracted information to a file."""
        print(f"Saving extracted information to {state.output_excel}")
        ExcelInfoSaver(state.output_excel, state.company, state.synthesized_info).save()
        return {
            "messages": [AIMessage(content=f"Saved extracted information to {state.output_excel}")]
        }

    async def router_decision(self, state: State):
        """Decide whether to end the search or continue."""
        if state.is_satisfactory == True or state.loop_count >= self.config.max_loops:
            return "end"
        else:
            return "search"

    def graph_building(self):
        self.workflow = StateGraph(
            State, config_schema=AgentConfig
        )
        self.workflow.add_node("search", self.search_urls)
        self.workflow.add_node("extract_info", self.extract_info)
        self.workflow.add_node("synthesize", self.synthesize_info)
        self.workflow.add_node("validate", self.validate_info)

        self.workflow.add_edge("__start__", "search")
        self.workflow.add_edge("search", "extract_info")
        self.workflow.add_edge("extract_info", "synthesize")
        self.workflow.add_edge("synthesize", "validate")
        self.workflow.add_conditional_edges(
            "validate",
            self.router_decision,
            {
                "end": END,  # End the search
                "search": "search"  # Restart the search
            }
        )
        graph = self.workflow.compile()
        return graph

    async def run(
        self, state: State, config: RunnableConfig
    ) -> Dict[str, Any]:
        """
        Executes the LangGraph workflow for the given state and configuration.

        :param state: The input state for the research process.
        :param config: Optional configuration for the workflow.
        :return: The output state after running the workflow.
        """
        print(f"Called run method")
        self.config = AgentConfig.from_runnable_config(config)
        self.prompt_manager = PromptManager(self.config)
        return await self.graph.ainvoke(state, {"recursion_limit": 100})
