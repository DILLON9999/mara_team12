from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.energy_tools import (
    LMPAnalyzerTool,
    BTCHashpriceTool,
    CarbonIntensityTool,
    MiningProfitCalculatorTool,
    ProfitCarbonAnalyzerTool,
    InferenceMarketTool,
    DashboardPublisherTool
)
from .tools.hardware_carbon_tools import (
    HardwareScoutTool,
    CarbonCreditTrackerTool,
    MinerEfficiencyAnalyzerTool,
    CarbonCreditRevenueTool
)

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class MaraHackathon():
    """Energy-Bitcoin Mining Optimization Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    @agent
    def market_intelligence_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['market_intelligence_agent'], # type: ignore[index]
            tools=[
                LMPAnalyzerTool(),
                BTCHashpriceTool(),
                InferenceMarketTool()
            ],
            verbose=True
        )

    @agent
    def environmental_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['environmental_analyst'], # type: ignore[index]
            tools=[
                CarbonIntensityTool()
            ],
            verbose=True
        )
    
    @agent
    def optimization_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['optimization_strategist'], # type: ignore[index]
            tools=[
                MiningProfitCalculatorTool(),
                ProfitCarbonAnalyzerTool()
            ],
            verbose=True
        )

    @agent
    def dashboard_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config['dashboard_publisher'], # type: ignore[index]
            tools=[
                DashboardPublisherTool()
            ],
            verbose=True
        )
    
    @agent
    def hardware_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['hardware_scout'], # type: ignore[index]
            tools=[
                HardwareScoutTool(),
                MinerEfficiencyAnalyzerTool()
            ],
            verbose=True
        )
    
    @agent
    def carbon_arbitrageur(self) -> Agent:
        return Agent(
            config=self.agents_config['carbon_arbitrageur'], # type: ignore[index]
            tools=[
                CarbonCreditTrackerTool(),
                CarbonCreditRevenueTool()
            ],
            verbose=True
        )

    # Tasks
    @task
    def market_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_analysis_task'], # type: ignore[index]
        )

    @task
    def carbon_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config['carbon_assessment_task'], # type: ignore[index]
        )
    
    @task
    def optimization_decision_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimization_decision_task'], # type: ignore[index]
        )
    
    @task
    def dashboard_update_task(self) -> Task:
        return Task(
            config=self.tasks_config['dashboard_update_task'], # type: ignore[index]
            output_file='mining_report.json'
        )
    
    @task
    def hardware_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['hardware_scout_task'], # type: ignore[index]
            output_file='hardware_update.json'
        )
    
    @task 
    def carbon_arbitrage_task(self) -> Task:
        return Task(
            config=self.tasks_config['carbon_arbitrage_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Energy-Bitcoin Mining Optimization crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
