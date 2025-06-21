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

@CrewBase
class MaraHackathon():
    """Energy-Bitcoin Mining Optimization Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
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

    @crew
    def crew(self) -> Crew:
        """Creates the Energy-Bitcoin Mining Optimization crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        ) 