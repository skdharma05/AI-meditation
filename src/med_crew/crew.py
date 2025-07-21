from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from med_crew.models import (
    MeditationStructure,
    MeditationSession,
    MeditationContent,
    MeditationTiming,
)
from med_crew.tools import (
    MeditationTimingTool,
    BreathingPatternTool,
    MeditationContentTool,
    JSONValidationTool,
    ActionParameterGeneratorTool,
)

from typing import List
import logging
from logging import getLogger

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Suppress non-app logs
logger = getLogger("app")
logger.setLevel(logging.DEBUG)
logger = getLogger("app")


@CrewBase
class MyCrew:
    """Meditation AI Crew for generating structured meditation sessions"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def meditation_designer(self) -> Agent:
        logger.debug("Initializing meditation_designer agent")
        return Agent(
            config=self.agents_config["meditation_designer"],  # type: ignore[index]
            verbose=True,
            tools=[MeditationTimingTool()],
        )

    @agent
    def content_creator(self) -> Agent:
        logger.debug("Initializing content_creator agent")
        return Agent(
            config=self.agents_config["content_creator"],  # type: ignore[index]
            verbose=True,
            tools=[MeditationContentTool(), BreathingPatternTool(), ActionParameterGeneratorTool()],
        )

    @agent
    def timing_specialist(self) -> Agent:
        logger.debug("Initializing timing_specialist agent")
        return Agent(
            config=self.agents_config["timing_specialist"],  # type: ignore[index]
            verbose=True,
            tools=[MeditationTimingTool(), BreathingPatternTool(), ActionParameterGeneratorTool()],
        )

    @agent
    def session_formatter(self) -> Agent:
        logger.debug("Initializing session_formatter agent")
        return Agent(
            config=self.agents_config["session_formatter"],  # type: ignore[index]
            verbose=True,
            tools=[JSONValidationTool(), ActionParameterGeneratorTool()],
        )

    @task
    def meditation_design_task(self) -> Task:
        logger.debug("Initializing meditation_design_task")
        return Task(
            config=self.tasks_config["meditation_design_task"],  # type: ignore[index]
            output_pydantic=MeditationStructure,  # Use the specific Pydantic model for this task
        )

    @task
    def content_creation_task(self) -> Task:
        logger.debug("Initializing content_creation_task")
        return Task(
            config=self.tasks_config["content_creation_task"],  # type: ignore[index]
            output_pydantic=MeditationContent,  # Use the specific Pydantic model for this task
        )

    @task
    def timing_orchestration_task(self) -> Task:
        logger.debug("Initializing timing_orchestration_task")
        return Task(
            config=self.tasks_config["timing_orchestration_task"],  # type: ignore[index]
            output_pydantic=MeditationTiming,  # Use the specific Pydantic model for this task
        )

    @task
    def session_formatting_task(self) -> Task:
        logger.debug("Initializing session_formatting_task")
        return Task(
            config=self.tasks_config["session_formatting_task"],  # type: ignore[index]
            output_pydantic=MeditationSession,  # Final output is validated and structured
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MyCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        logger.debug("Creating the MyCrew crew")
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
