# MyCrew Crew

Welcome to the MyCrew Crew project, powered by [crewAI](https://crewai.com). This project enables you to set up a multi-agent AI system for generating structured meditation sessions. With crewAI, your agents collaborate effectively to achieve complex tasks, leveraging their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling.

### Steps to Install

1. Install `uv` if you haven't already:

   ```bash
   pip install uv
   ```

2. Navigate to your project directory and install the dependencies:

   ```bash
   uv install
   ```

3. (Optional) Lock the dependencies and install them using the CLI command:

   ```bash
   crewai install
   ```

### Configuration

- Add your `OPENAI_API_KEY` to the `.env` file.
- Modify the following files to customize your agents and tasks:
  - `src/my_crew/config/agents.yaml`: Define your agents.
  - `src/my_crew/config/tasks.yaml`: Define your tasks.
  - `src/my_crew/crew.py`: Add your own logic, tools, and specific arguments.
  - `src/my_crew/main.py`: Add custom inputs for your agents and tasks.

## Running the Project

To start the application in development mode, run the following command from the root folder of your project:

```bash
uv run uvicorn my_crew.api:app --reload
```

This command initializes the MyCrew Crew, assembling the agents and assigning them tasks as defined in your configuration.

## Project Overview

The MyCrew Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks to generate structured meditation sessions. The key components of the project are:

- **Agents**: Defined in `config/agents.yaml`, each agent has a specific role and goal.
- **Tasks**: Defined in `config/tasks.yaml`, tasks outline the objectives and expected outputs.
- **Crew Logic**: Implemented in `src/my_crew/crew.py`, this file orchestrates the agents and tasks.
- **Meditation Models**: Located in `src/my_crew/models.py`, these define the schemas for meditation sessions, content, and timing.

## Example Output

By default, running the project will generate structured meditation sessions based on the provided configurations. These sessions are designed to include detailed scripts, precise timing, and agent coordination for a seamless meditation experience.

## Support

For support, questions, or feedback regarding the MyCrew Crew or crewAI:

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
