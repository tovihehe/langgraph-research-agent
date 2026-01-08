import sys
import os
import yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.research_agent.agent import ResearcherAgent
from agents.research_agent.state import State
from langchain_core.runnables import RunnableConfig
import asyncio
import time
import datetime

async def test():
    """Test the agent."""
    
    # topic = "Casos de uso de agentes en el MWC Barcelona 2025"
    topic = input("Enter the topic to research: ")


    # Load the YAML file into a dictionary
    print("Loading config data...")
    with open("config/research_agent_config.yaml", "r") as file:
        config_data = yaml.safe_load(file)


    # Create a RunnableConfig object. The key "configurable" is expected by AgentConfig.from_runnable_config
    runnable_config = RunnableConfig(configurable=config_data)

    # Create a sample config
    agent = ResearcherAgent()

    test_state = State(
            topic=topic
        )
    
    output_state = await agent.run(test_state, config=runnable_config)
    print("----------------------------------------------------------------------------------------------------------------------------------------")
    output_dictionary = output_state["synthesized_info"]["content"]
    print("Synthesized information:")
    print(output_dictionary)

    print("----------------------------------------------------------------------------------------------------------------------------------------")

async def company_research():
    """Test the agent."""
    input_excel = "research_questions.xlsx"

    # Load the YAML file into a dictionary
    print("Loading config data...")
    with open("config/research_agent_config.yaml", "r") as file:
        config_data = yaml.safe_load(file)

    # Create a RunnableConfig object. The key "configurable" is expected by AgentConfig.from_runnable_config
    runnable_config = RunnableConfig(configurable=config_data)

    # Create a sample config
    agent = ResearcherAgent()

    # Do date_time formatting
    output_excel = "companies_research_"+ datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".xlsx"

    # Companies to research
    companies = ["Veolia", "Airpharm Logistics", "Celsa", "Insudpharma", "Tous", "Laboratorios Rovi", "Bon Preu", "Bacardi", "Damm", "Cbre", "Aedas Home", "Carrefour", "Dkv Seguros Salud", "Acesur", "Asisa", "Intrum",  "Grupo Consorcio Conservas", "Refrival", "Unicaja", "Diglo Servicer", "Bankinter", "Ayvens", "Mutua Madrileña", "El Corte Inglés", "Seguros Santalucia", "Ferrovial"]
   
    for company in companies:
        print(f"Researching {company}...")
        # Create a new state for each company
        test_state = State(
            topic=company+" info",
            company=company,
            output_excel=output_excel,  
            input_excel=input_excel 
        )

        # Run the workflow with the first test state
        output_state = await agent.run(test_state, config=runnable_config)

        print("----------------------------------------------------------------------------------------------------------------------------------------")
        for message in output_state["messages"]:
            print(message.content)

async def main():
    """Run the test with a timeout of 90 minutes."""
    try:
        start_time = time.time()
        print("Starting test...")
        await asyncio.wait_for(test(), timeout=120)
        print(f"Test completed successfully in {time.time() - start_time:.2f} seconds")
    except asyncio.TimeoutError:
        print("Test timed out")

asyncio.run(main())
