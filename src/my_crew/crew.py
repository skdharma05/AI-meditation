from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class MyCrew():
    """Meditation AI Crew for generating structured meditation sessions"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def meditation_script_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['meditation_script_generator'], # type: ignore[index]
            verbose=True
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def timing_orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config['timing_orchestrator'], # type: ignore[index]
            verbose=True
        )


    @agent
    def json_formatter(self) -> Agent:
        # Use a standard Agent, post-process output in the API or after agent run
        return Agent(
            config=self.agents_config['json_formatter'], # type: ignore[index]
            verbose=True
        )

    @task
    def meditation_design_task(self) -> Task:
        from my_crew.models import MeditationStructure
        return Task(
            config=self.tasks_config['meditation_design_task'], # type: ignore[index]
            output_type=dict,  # Explicitly output JSON/dict for agent-to-agent communication
            output_pydantic=MeditationStructure  # Use the specific Pydantic model for this task
        )

    @task
    def content_creation_task(self) -> Task:
        from my_crew.models import MeditationContent
        return Task(
            config=self.tasks_config['content_creation_task'], # type: ignore[index]
            output_type=dict,  # Explicitly output JSON/dict for agent-to-agent communication
            output_pydantic=MeditationContent  # Use the specific Pydantic model for this task
        )

    @task
    def timing_orchestration_task(self) -> Task:
        from my_crew.models import MeditationTiming
        return Task(
            config=self.tasks_config['timing_orchestration_task'], # type: ignore[index]
            output_type=dict,  # Explicitly output JSON/dict for agent-to-agent communication
            output_pydantic=MeditationTiming  # Use the specific Pydantic model for this task
        )

    @task
    def json_generation_task(self) -> Task:
        from my_crew.models import MeditationSession
        return Task(
            config=self.tasks_config['json_generation_task'], # type: ignore[index]
            output_file='meditation_session.json',
            output_type=dict,  # Explicitly output JSON/dict
            output_pydantic=MeditationSession  # Final output is validated and structured
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MyCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
